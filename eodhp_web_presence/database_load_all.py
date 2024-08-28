import logging
import os
import subprocess
import sys
import tempfile

import boto3

pg_load_path = "psql"

bucket_name = "web-database-exports"

temp_schema_name = "base_content"


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

        source = file.split("-")[0]
        target = os.environ["ENV_NAME"]

        output_file = "new_schema.sql"
        with open(output_file, "w") as f:
            for line in open(f"{tmpdir}/{file}").readlines():
                line = line.replace(f"{source}.", f"{target}.")
                f.write(line)

        load_command = (
            f"{pg_load_path} "
            f'-U {os.environ["SQL_USER"]} '
            f'-h {os.environ["SQL_HOST"]} '
            f'-p {os.environ["SQL_PORT"]} '
            f'-d {os.environ["SQL_DATABASE"]} '
            f"-f {output_file} "
            f"--single-transaction"
        )
        set_admin_command = (
            f"UPDATE {temp_schema_name}.accounts_user SET password=password, is_active=false;"
        )
        change_schema_name_back_command = (
            f'ALTER SCHEMA {temp_schema_name} RENAME TO {os.environ["ENV_NAME"]}'
        )

        os.environ["PGPASSWORD"] = os.environ["SQL_PASSWORD"]

        logging.info(f"Running: {load_command}")
        subprocess.run(load_command, shell=True, check=True)
        logging.info(f"Running: {set_admin_command}")
        subprocess.run(run_sql_command(set_admin_command), shell=True, check=True)
        logging.info(f"Running: {change_schema_name_back_command}")
        subprocess.run(run_sql_command(change_schema_name_back_command), shell=True, check=True)

        del os.environ["PGPASSWORD"]

        logging.info("Complete")
