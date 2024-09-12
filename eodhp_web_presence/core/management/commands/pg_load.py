import glob
import logging
import os
import shutil
import subprocess
import sys
import tempfile

import boto3
from django.core.management.base import BaseCommand

from eodhp_web_presence import settings

pg_load_path = "psql"

media_bucket_name = os.environ["AWS_STORAGE_BUCKET_NAME"]

temp_schema_name = "base_content"


def copy_files(source_bucket_name: str, target_bucket_name, folder_name: str):
    """Copy files from one S3 bucket to another"""
    logging.info(f"Copying files from {source_bucket_name} into {target_bucket_name}")

    s3_client = boto3.client("s3")
    for key in s3_client.list_objects(Bucket=source_bucket_name, Prefix=folder_name)["Contents"]:
        path = key["Key"]
        new_path = "/".join(path.split("/")[2:])

        if new_path:  # ignores anything in the top level e.g. SQL exports
            s3_client.copy_object(
                CopySource=f"/{source_bucket_name}/{path}",
                Bucket=target_bucket_name,
                Key=f'{os.environ["MEDIAFILES_LOCATION"]}/{new_path}',
            )
    logging.info(f"Copying files from {source_bucket_name} into {target_bucket_name} complete")


def upload_files(export_bucket_name: str, media_bucket_name: str, folder_name: str):
    """Updates files in S3 from local directory"""
    logging.info(f"Copying files from {export_bucket_name} into {media_bucket_name}")
    s3 = boto3.resource("s3")

    root = f"{export_bucket_name}/{folder_name}/"
    for local_file_path in glob.glob(f"{root}*-static-apps/**", recursive=True):
        s3_path = local_file_path.replace(root, "")
        s3_path = os.environ["ENV_NAME"] + "-" + "-".join(s3_path.split("-")[1:])
        try:
            s3.Bucket(media_bucket_name).upload_file(local_file_path, s3_path)
        except IsADirectoryError:
            pass


def run_sql_command(sql: str) -> str:
    return (
        f"{pg_load_path} "
        f'-U {settings.DATABASES["default"]["USER"]} '
        f'-h {settings.DATABASES["default"]["HOST"]} '
        f'-p {settings.DATABASES["default"]["PORT"]} '
        f'-d {settings.DATABASES["default"]["NAME"]} '
        f"-c '{sql}'"
    )


def pg_load(export_bucket_name: str, folder_name: str, load_media_folder: bool, use_s3):
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("database_load").setLevel(logging.DEBUG)

    database_dump_file = "wagtail_dump.sql"

    if os.getenv("AWS_ACCESS_KEY") and os.getenv("AWS_SECRET_ACCESS_KEY"):
        session = boto3.session.Session(
            aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )
        s3 = session.client("s3")

    else:
        s3 = boto3.client("s3")

    with tempfile.TemporaryDirectory() as tmpdir:
        logging.info(f"Collecting {folder_name}/{database_dump_file} from {export_bucket_name}")
        if use_s3:
            s3.download_file(
                export_bucket_name,
                f"{folder_name}/{database_dump_file}",
                f"{tmpdir}/{database_dump_file}",
            )
        else:
            shutil.copy(
                f"{export_bucket_name}/{folder_name}/{database_dump_file}",
                f"{tmpdir}/{database_dump_file}",
            )

        load_command = (
            f"{pg_load_path} "
            f'-U {settings.DATABASES["default"]["USER"]} '
            f'-h {settings.DATABASES["default"]["HOST"]} '
            f'-p {settings.DATABASES["default"]["PORT"]} '
            f'-d {settings.DATABASES["default"]["NAME"]} '
            f"-f {tmpdir}/{database_dump_file} "
            f"--single-transaction"
        )
        change_schema_name_back_command = (
            f'ALTER SCHEMA {temp_schema_name} RENAME TO {os.environ["ENV_NAME"]}'
        )

        os.environ["PGPASSWORD"] = os.environ["SQL_PASSWORD"]

        logging.info(f"Running: {load_command}")
        subprocess.run(load_command, shell=True, check=True)  # nosec

        set_admin_command = (
            f"UPDATE {temp_schema_name}.accounts_user SET " f"password='password', is_active=false;"
        )
        logging.info(f"Running: {set_admin_command}")
        subprocess.run(run_sql_command(set_admin_command), shell=True, check=True)  # nosec

        logging.info(f"Running: {change_schema_name_back_command}")
        subprocess.run(
            run_sql_command(change_schema_name_back_command),
            shell=True,  # nosec
            check=True,
        )

        del os.environ["PGPASSWORD"]

        if load_media_folder:
            if use_s3:
                copy_files(export_bucket_name, media_bucket_name, folder_name)
            else:
                upload_files(export_bucket_name, media_bucket_name, folder_name)

        logging.info("Complete")


class Command(BaseCommand):
    help = "Load CMS from S3"

    def add_arguments(self, parser):
        parser.add_argument("folder_name", type=str, default=None)
        parser.add_argument("-b", "--bucket-name", type=str, default=None)

        parser.add_argument("-m", "--load-media-folder", type=str, default="1")
        parser.add_argument("-s3", "--use-s3", type=str, default="1")

    def handle(self, *args, **kwargs):
        bucket_name = kwargs["bucket_name"]
        folder_name = kwargs["folder_name"]
        load_media_folder = kwargs["load_media_folder"].lower() in ["true", "1", "t", "y", "yes"]
        use_s3 = kwargs["use_s3"].lower() in ["true", "1", "t", "y", "yes"]

        if not folder_name:
            logging.error(
                f"Backup name within {os.environ['AWS_STORAGE_EXPORT_BUCKET_NAME']} not specified. \n"
                f"Run with python manage.py my_backup_folder"
            )
            sys.exit(1)

        if not bucket_name:
            bucket_name = os.environ["AWS_STORAGE_EXPORT_BUCKET_NAME"]

        pg_load(bucket_name, folder_name, load_media_folder, use_s3)
