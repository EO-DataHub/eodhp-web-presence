import logging
import os
import subprocess
import sys
import tempfile

import boto3

table_prefixes = ["home", "help", "wagtailimages", "wagtailcore"]

pg_load_path = "pg_restore"

bucket_name = "web-database-exports"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("database_dump").setLevel(logging.DEBUG)

    try:
        file = sys.argv[1]
    except IndexError:
        logging.error("File name not specified")

    if os.getenv("AWS_ACCESS_KEY") and os.getenv("AWS_SECRET_ACCESS_KEY"):
        session = boto3.session.Session(
            aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )
        s3 = session.client("s3")

    else:
        s3 = boto3.client("s3")

    s3_object = s3.get_object(Bucket=bucket_name, Key=file)

    with tempfile.TemporaryDirectory() as tmpdir:
        logging.info(f"Collecting {file} from {bucket_name}")
        s3.download_file(bucket_name, file, f"{tmpdir}/{file}")

        command = f'{pg_load_path} -c -U {os.environ["SQL_USER"]} -h {os.environ["SQL_HOST"]} -p {os.environ["SQL_PORT"]} -d {os.environ["SQL_DATABASE"]} < {tmpdir}/{file}'  # noqa: E501

        logging.info(f"Running: {command}")
        os.environ["PGPASSWORD"] = os.environ["SQL_PASSWORD"]
        subprocess.run(command, shell=True, check=True)  # nosec B602
        del os.environ["PGPASSWORD"]

        logging.info("Complete")
