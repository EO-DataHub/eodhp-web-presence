import logging
import os
import subprocess
import sys
import tempfile

import boto3
import psycopg2

table_prefixes = ["home", "wagtailimages", "wagtailcore"]

bucket_name = "web-database-exports"


def truncate_tables() -> str:
    conn = psycopg2.connect(
        dbname=os.environ["SQL_DATABASE"],
        user=os.environ["SQL_USER"],
        password=os.environ["SQL_PASSWORD"],
        host=os.environ["SQL_HOST"],
        port=os.environ["SQL_PORT"],
    )

    cur = conn.cursor()

    table_names = []

    for prefix in table_prefixes:
        cur.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname = %s AND tablename LIKE %s;",
            (os.environ["ENV_NAME"], prefix + "%",),
        )
        table_names.extend([row[0] for row in cur.fetchall()])

    for table in table_names:
        if not table == "wagtailcore_locale":
            logging.info(f"Truncating {table}")
            try:
                cur.execute(f"TRUNCATE TABLE {table} CASCADE;")
                conn.commit()
            except psycopg2.errors.UndefinedTable:
                logging.info(
                    f"Error truncating {table} - check that it exists and consider deleting unused table from original database"  # noqa: E501
                )
                conn.rollback()

    cur.close()
    conn.close()


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

        truncate_tables()

        command = f"python manage.py loaddata {tmpdir}/{file}"

        logging.info(f"Running: {command}")
        subprocess.run(command, shell=True, check=True)

        logging.info("Complete")
