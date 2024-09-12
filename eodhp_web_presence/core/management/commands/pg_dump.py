import datetime
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import boto3
from django.core.management.base import BaseCommand

from eodhp_web_presence import settings

pg_dump_path = "pg_dump"

media_bucket_name = os.environ["AWS_STORAGE_BUCKET_NAME"]

temp_schema_name = "base_content"


def upload_sql_file(path: str, folder: str, s3_bucket_name: str, s3: boto3.resource) -> None:
    """Updates SQL file in S3 from local directory"""
    logging.info(f"Updating {path} into {folder} in {s3_bucket_name}")

    s3.Bucket(s3_bucket_name).upload_file(f"{path}", f"{folder}/{path}")


def save_sql_file_locally(path: str, folder: str, target_folder_name: str) -> None:
    """Updates SQL file in local folder"""
    logging.info(f"Updating {path} into {folder} in {target_folder_name}")

    shutil.copyfile(path, f"{target_folder_name}/{folder}/{path}")


def copy_files(source_bucket_name: str, target_bucket_name, output_folder_name: str):
    """Copies S3 files from one bucket to another"""
    logging.info(
        f"Copying files from {source_bucket_name} into {output_folder_name} in {target_bucket_name}"
    )

    s3_client = boto3.client("s3")
    for key in s3_client.list_objects(Bucket=source_bucket_name)["Contents"]:
        path = key["Key"]
        s3_client.copy_object(
            CopySource=f"/{source_bucket_name}/{path}",
            Bucket=target_bucket_name,
            Key=f"{output_folder_name}/{path}",
        )
    logging.info(f"Copying files from {source_bucket_name} to {target_bucket_name} complete")


def copy_files_locally(source_bucket_name: str, target_folder_name, output_folder_name: str):
    """Copies S3 files into a local directory"""
    logging.info(
        f"Copying files from {source_bucket_name} into {output_folder_name} in {target_folder_name}"
    )

    s3 = boto3.resource("s3")

    bucket = s3.Bucket(source_bucket_name)
    bucket_contents = list(bucket.objects.filter())

    folder_path = f"{target_folder_name}/{output_folder_name}"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for item in bucket_contents:
        obj_path = os.path.dirname(f"{folder_path}/{item.key}")
        try:
            Path(obj_path).mkdir(parents=True, exist_ok=True)
            bucket.download_file(item.key, f"{folder_path}/{item.key}".replace("//", "/"))
        except FileExistsError:
            pass  # duplicate key

    logging.info(f"Copying files from {source_bucket_name} to {target_folder_name} complete")


def run_sql_command(sql: str) -> str:
    return (
        f"psql "
        f'-U {settings.DATABASES["default"]["USER"]} '
        f'-h {settings.DATABASES["default"]["HOST"]} '
        f'-p {settings.DATABASES["default"]["PORT"]} '
        f'-d {settings.DATABASES["default"]["NAME"]} '
        f"-c '{sql}'"
    )


def pg_dump(output_bucket_name: str, output_folder_name: str, backup_media_folder: bool, use_s3):
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("database_dump").setLevel(logging.DEBUG)

    if os.getenv("AWS_ACCESS_KEY") and os.getenv("AWS_SECRET_ACCESS_KEY"):
        session = boto3.session.Session(
            aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )
        s3 = session.resource("s3")

    else:
        s3 = boto3.resource("s3")

    output_file = "wagtail_dump.sql"

    with tempfile.NamedTemporaryFile() as tf:
        tf.name = output_file

        change_schema_name_command = (
            f'ALTER SCHEMA {os.environ["ENV_NAME"]} RENAME TO {temp_schema_name}'
        )
        dump_command = (
            f"{pg_dump_path} "
            f'-U {settings.DATABASES["default"]["USER"]} '
            f'-h {settings.DATABASES["default"]["HOST"]} '
            f'-p {settings.DATABASES["default"]["PORT"]} '
            f'-d {settings.DATABASES["default"]["NAME"]} '
            f"-n {temp_schema_name} "
            f"-f {output_file}"
        )
        change_schema_name_back_command = (
            f'ALTER SCHEMA {temp_schema_name} RENAME TO {os.environ["ENV_NAME"]}'
        )

        os.environ["PGPASSWORD"] = os.environ["SQL_PASSWORD"]

        try:
            logging.info(f"Running: {change_schema_name_command}")
            subprocess.run(
                run_sql_command(change_schema_name_command), shell=True, check=True  # nosec
            )
            logging.info(f"Running: {dump_command}")
            subprocess.run(dump_command, shell=True, check=True)  # nosec
        except Exception as e:
            logging.error(e)
        finally:
            logging.info(f"Running: {change_schema_name_back_command}")
            subprocess.run(
                run_sql_command(change_schema_name_back_command), shell=True, check=True  # nosec
            )

        del os.environ["PGPASSWORD"]

        if use_s3:
            if backup_media_folder:
                copy_files(media_bucket_name, output_bucket_name, output_folder_name)

            upload_sql_file(output_file, output_folder_name, output_bucket_name, s3)

        else:
            if backup_media_folder:
                copy_files_locally(media_bucket_name, output_bucket_name, output_folder_name)

            save_sql_file_locally(output_file, output_folder_name, output_bucket_name)

        logging.info("Complete")


class Command(BaseCommand):
    help = "Dump contents of CMS database and media"

    def add_arguments(self, parser):
        parser.add_argument("-b", "--bucket-name", type=str, default=None)
        parser.add_argument("-f", "--folder-name", type=str)
        parser.add_argument("-m", "--backup-media-folder", type=str, default="1")
        parser.add_argument("-s3", "--use-s3", default="1", type=str)

    def handle(self, *args, **kwargs):
        bucket_name = kwargs["bucket_name"]
        folder_name = kwargs["folder_name"]
        backup_media_folder = kwargs["backup_media_folder"].lower() in [
            "true",
            "1",
            "t",
            "y",
            "yes",
        ]
        use_s3 = kwargs["use_s3"].lower() in ["true", "1", "t", "y", "yes"]

        if not folder_name:
            folder_name = (
                f'{os.environ.get("ENV_NAME", "default")}-'
                f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
            )

        if not bucket_name:
            bucket_name = os.environ["AWS_STORAGE_EXPORT_BUCKET_NAME"]

        pg_dump(bucket_name, folder_name, backup_media_folder, use_s3)
