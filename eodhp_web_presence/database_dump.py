import datetime
import logging
import os
import subprocess
import tempfile

import boto3

pg_dump_path = "pg_dump"

export_bucket_name = os.environ["AWS_STORAGE_EXPORT_BUCKET_NAME"]
media_bucket_name = os.environ["AWS_STORAGE_BUCKET_NAME"]

temp_schema_name = "base_content"


def upload_sql_file(path: str, folder: str, s3_bucket_name: str, s3: boto3.resource) -> None:
    """Updates file in S3 from local directory"""
    logging.info(f"Updating {path} into {folder} in {s3_bucket_name}")

    s3.Bucket(s3_bucket_name).upload_file(f"{path}", f"{folder}/{path}")


def copy_files(source_bucket_name: str, target_bucket_name, output_folder_name: str):
    logging.info(
        f"Copying files from {source_bucket_name} into {output_folder_name} in {target_bucket_name}"
    )

    s3_client = boto3.client("s3")
    """Updates file in S3 from local directory"""
    for key in s3_client.list_objects(Bucket=source_bucket_name)["Contents"]:
        path = key["Key"]
        s3_client.copy_object(
            CopySource=f"/{source_bucket_name}/{path}",
            Bucket=target_bucket_name,
            Key=f"{output_folder_name}/{path}",
        )
    logging.info(f"Copying files from {source_bucket_name} to {target_bucket_name} complete")


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
    logging.getLogger("database_dump").setLevel(logging.DEBUG)

    if os.getenv("AWS_ACCESS_KEY") and os.getenv("AWS_SECRET_ACCESS_KEY"):
        session = boto3.session.Session(
            aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )
        s3 = session.resource("s3")

    else:
        s3 = boto3.resource("s3")

    output_folder_name = f'{os.environ.get("ENV_NAME", "default")}-{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'  # # noqa: E501

    output_file = "wagtail_dump.sql"

    with tempfile.NamedTemporaryFile() as tf:
        tf.name = output_file

        change_schema_name_command = (
            f'ALTER SCHEMA {os.environ["ENV_NAME"]} RENAME TO {temp_schema_name}'
        )
        dump_command = (
            f"{pg_dump_path} "
            f'-U {os.environ["SQL_USER"]} '
            f'-h {os.environ["SQL_HOST"]} '
            f'-p {os.environ["SQL_PORT"]} '
            f'-d {os.environ["SQL_DATABASE"]} '
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

        copy_files(media_bucket_name, export_bucket_name, output_folder_name)

        upload_sql_file(output_file, output_folder_name, export_bucket_name, s3)
        logging.info("Complete")
