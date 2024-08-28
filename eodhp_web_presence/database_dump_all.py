import datetime
import logging
import os
import subprocess
import tempfile

import boto3

pg_dump_path = "pg_dump"

bucket_name = "web-database-exports"

temp_schema_name = "base_content"


def update_file(path: str, s3_bucket_name: str, s3: boto3.resource) -> None:
    """Updates file in S3 from local directory"""
    logging.info(f"Updating {path} into {s3_bucket_name}")

    s3.Bucket(s3_bucket_name).upload_file(f"{path}", f"{path}")


def run_sql_command(sql: str) -> str:
    return f'psql -U {os.environ["SQL_USER"]} -h {os.environ["SQL_HOST"]} -p {os.environ["SQL_PORT"]} -d {os.environ["SQL_DATABASE"]} -c \'{sql}\''


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

    output_file = f'{os.environ.get("ENV_NAME", "default")}-wagtail_dump-{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'  # noqa: E501

    with tempfile.NamedTemporaryFile() as tf:
        tf.name = output_file

        change_schema_name_command = f'ALTER SCHEMA {os.environ["ENV_NAME"]} RENAME TO {temp_schema_name}'
        dump_command = f'{pg_dump_path} -U {os.environ["SQL_USER"]} -h {os.environ["SQL_HOST"]} -p {os.environ["SQL_PORT"]} -d {os.environ["SQL_DATABASE"]} -n {temp_schema_name} -f {output_file}'  # noqa: E501
        change_schema_name_back_command = f'ALTER SCHEMA {temp_schema_name} RENAME TO {os.environ["ENV_NAME"]}'

        os.environ["PGPASSWORD"] = os.environ["SQL_PASSWORD"]

        try:
            logging.info(f"Running: {change_schema_name_command}")
            subprocess.run(run_sql_command(change_schema_name_command), shell=True, check=True)
            logging.info(f"Running: {dump_command}")
            subprocess.run(dump_command, shell=True, check=True)
        except Exception as e:
            logging.error(e)
        finally:
            logging.info(f"Running: {change_schema_name_back_command}")
            subprocess.run(run_sql_command(change_schema_name_back_command), shell=True, check=True)

        del os.environ["PGPASSWORD"]

        update_file(output_file, bucket_name, s3)
        logging.info("Complete")
