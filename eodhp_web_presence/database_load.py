import logging
import os
import subprocess
import sys
import tempfile

import boto3

pg_load_path = "psql"

bucket_name = "web-database-exports"

export_bucket_name = os.environ["AWS_STORAGE_EXPORT_BUCKET_NAME"]
media_bucket_name = os.environ["AWS_STORAGE_BUCKET_NAME"]

temp_schema_name = "base_content"


def copy_files(source_bucket_name: str, target_bucket_name, folder_name: str):
    logging.info(f"Copying files from {source_bucket_name} into {target_bucket_name}")

    s3_client = boto3.client("s3")
    """Updates file in S3 from local directory"""
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


def run_sql_command(sql: str) -> str:
    return (
        f"psql "
        f'-U {os.environ["SQL_USER"]} '
        f'-h {os.environ["SQL_HOST"]} '
        f'-p {os.environ["SQL_PORT"]} '
        f'-d {os.environ["SQL_DATABASE"]} '
        f"-c '{sql}'"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("database_load").setLevel(logging.DEBUG)

    try:
        folder = sys.argv[1]
    except IndexError:
        logging.error(
            f"Backup name within {os.environ['AWS_STORAGE_EXPORT_BUCKET_NAME']} not specified. \n"
            f"Run with python database_load.py my_backup_folder"
        )
        sys.exit(1)

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
        logging.info(f"Collecting {folder}/{database_dump_file} from {export_bucket_name}")
        s3.download_file(
            export_bucket_name, f"{folder}/{database_dump_file}", f"{tmpdir}/{database_dump_file}"
        )

        target = os.environ["ENV_NAME"]

        load_command = (
            f"{pg_load_path} "
            f'-U {os.environ["SQL_USER"]} '
            f'-h {os.environ["SQL_HOST"]} '
            f'-p {os.environ["SQL_PORT"]} '
            f'-d {os.environ["SQL_DATABASE"]} '
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

        copy_files(export_bucket_name, media_bucket_name, folder)

        logging.info("Complete")
