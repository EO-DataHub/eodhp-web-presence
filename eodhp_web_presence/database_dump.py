import datetime
import logging
import os
import subprocess
import tempfile

import boto3

bucket_name = "web-database-exports"


def update_file(path: str, s3_bucket_name: str, s3: boto3.resource) -> None:
    """Updates file in S3 from local directory"""
    logging.info(f"Updating {path} into {s3_bucket_name}")

    s3.Bucket(s3_bucket_name).upload_file(f"{path}", f"{path}")


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

        command = f"python manage.py dumpdata home wagtailimages wagtailcore --natural-primary --natural-foreign --exclude auth --exclude contenttypes --exclude sessions > {output_file}"  # noqa: E501

        logging.info(f"Running: {command}")
        subprocess.run(command, shell=True, check=True)

        logging.info(f"Updating {output_file} into {bucket_name}")
        update_file(output_file, bucket_name, s3)
        logging.info("Complete")
