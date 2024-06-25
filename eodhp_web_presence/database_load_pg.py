import logging
import os
import subprocess
import tempfile

import boto3
import psycopg2


table_prefixes = ["home", "help"]

pg_load_path = "pg_restore"

bucket_name = "hc-test-bucket-can-be-deleted"


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


def match_file(path: str, s3_contents: list, folder: str, s3_folder: str):
    """Checks to see if file already exists in S3"""
    subdir = f"{s3_folder}/" if s3_folder else ""
    file_path = f"{subdir}{path}"

    if os.path.exists(f"{folder}/{path}") and not os.path.isdir(f"{folder}/{path}"):
        return next((f for f in s3_contents if f.key == file_path), None)
    else:
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("database_dump").setLevel(logging.DEBUG)

    if os.getenv("AWS_ACCESS_KEY") and os.getenv("AWS_SECRET_ACCESS_KEY"):
        session = boto3.session.Session(
            aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )
        s3 = session.client("s3")

    else:
        s3 = boto3.client("s3")

    file = "dev-wagtail_dump-20240621_155130.sql"

    s3_object = s3.get_object(Bucket=bucket_name, Key=file)

    with tempfile.TemporaryDirectory() as tmpdir:
        s3.download_file(bucket_name, file, f"{tmpdir}/{file}")

        command = f'{pg_load_path} -c -U {os.environ["SQL_USER"]} -h {os.environ["SQL_HOST"]} -p {os.environ["SQL_PORT"]} -d {os.environ["SQL_DATABASE"]} < {tmpdir}/{file}'  # noqa: E501

        os.environ["PGPASSWORD"] = SQL_PASSWORD
        subprocess.run(command, shell=True, check=True)
        del os.environ["PGPASSWORD"]
