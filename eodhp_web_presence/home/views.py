"""
Still a proof of concept. 

This view is intended to be used to generate temporary credentials for a user to access their associated S3 access point.

To complete this we need to ensure that we can retrieve the following from the users session:
- username
- access_point_arn 
- workspace_access_role_arn 

"""

import logging

import boto3
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def check_user_has_access_point_access(username):
    access_point_arn = f"arn:aws:s3:eu-west-2:#:accesspoint/eodhp-dev-y4jfxod4-{username}-s3"  # TODO: Hardcoded for now, in future this will come from the users session.
    s3_client = boto3.client(
        "s3",
    )
    response = s3_client.list_objects_v2(Bucket=access_point_arn)
    return response


def get_temp_credentials(request):
    username = request.GET.get("username")

    if not username:
        return JsonResponse({"error": "The username parameter is required."}, status=400)

    workspace_access_role_arn = "arn:aws:iam::#:role/#"  # TODO: Hardcoded for now, in future this will come from the users session.
    session_name = f"WorkspaceSession-{username}"  # Attaching the username to the session name to make it auditable

    try:
        sts_client = boto3.client("sts")
        assumed_role = sts_client.assume_role(
            RoleArn=workspace_access_role_arn,
            RoleSessionName=session_name,
            DurationSeconds=3600,  # TODO: We need to allow role permissions to extend longer than 3600
        )
        credentials = assumed_role["Credentials"]

        # Check that the user is allowed to access the S3 access point
        check_user_has_access_point_access(username, credentials)

        return JsonResponse(
            {
                "AccessKeyId": credentials["AccessKeyId"],
                "SecretAccessKey": credentials["SecretAccessKey"],
                "SessionToken": credentials["SessionToken"],
            }
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse(
            {
                "error": "The username provided is incorrect or does not have relevant permissions. Please try again later."
            },
            status=500,
        )
