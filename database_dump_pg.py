import datetime
import logging
import os
import subprocess
import tempfile

import boto3
import psycopg2

SQL_ENGINE = "django.db.backends.postgresql_psycopg2"
SQL_DATABASE = "wagtail_pgdb"
SQL_USER = "postgres"
SQL_PASSWORD = "password"
SQL_HOST = "localhost"
SQL_PORT = "5432"

table_prefixes = ["home", "help"]

pg_dump_path = "pg_dump"

bucket_name = 'hc-test-bucket-can-be-deleted'


def get_tables():
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
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename LIKE %s;",
            (prefix + "%",),
        )
        table_names.extend([row[0] for row in cur.fetchall()])

    cur.close()
    conn.close()

    return " ".join(f"-t {table}" for table in table_names)


def update_file(
    path: str, s3_bucket_name: str, s3: boto3.resource
) -> None:
    """Updates file in S3 from local directory"""
    logging.info(f"Updating {path} into {s3_bucket_name}")

    s3.Bucket(s3_bucket_name).upload_file(f"{path}", f"{path}")


if __name__ == '__main__':
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

    tables_str = get_tables()

    output_file = f'{os.environ.get("ENV_NAME", "default")}-wagtail_dump-{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'

    with tempfile.NamedTemporaryFile() as tf:
        tf.name = output_file

        command = f"{pg_dump_path} -U {SQL_USER} -h {SQL_HOST} -p {SQL_PORT} -d {SQL_DATABASE} {tables_str} -F c -f {output_file}"

        os.environ["PGPASSWORD"] = SQL_PASSWORD
        subprocess.run(command, shell=True, check=True)
        del os.environ["PGPASSWORD"]

        update_file(output_file, bucket_name, s3)
