import datetime
import logging
import os
import subprocess
import tempfile

import boto3

bucket_name = "web-database-exports"


def update_file(path: str, file_name: str, s3_bucket_name: str, s3: boto3.resource) -> None:
    """Updates file in S3 from local directory"""
    logging.info(f"Updating {path} into {s3_bucket_name}")

    s3.Bucket(s3_bucket_name).upload_file(path, file_name)


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

    file_name = f'{os.environ.get("ENV_NAME", "default")}-wagtail_dump-{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json'  # noqa: E501

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = f"{tmpdir}/{file_name}"
        command = f"python manage.py dumpdata home wagtailimages wagtailcore --natural-primary --natural-foreign --exclude auth --exclude contenttypes --exclude sessions > {file_path}"  # noqa: E501

        logging.info(f"Running: {command}")
        subprocess.run(command, shell=True, check=True)

        update_file(file_path, file_name, bucket_name, s3)
        logging.info("Complete")
