import json
import os
import re
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])

ID_PATTERN = re.compile(r"^[A-Za-z0-9]{6}$")


def respond(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    short_id = (event.get("pathParameters") or {}).get("short_id")
    if not short_id:
        return respond(400, {"error": "Missing short ID"})

    # Malformed IDs can never exist, so skip the database call.
    if not ID_PATTERN.match(short_id):
        return respond(404, {"error": "Short link not found"})

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        # One call: look the link up AND count the click.
        # The condition makes it fail (instead of creating a row) for unknown IDs.
        result = table.update_item(
            Key={"short_id": short_id},
            UpdateExpression="SET clicks = if_not_exists(clicks, :zero) + :one, last_accessed = :now",
            ConditionExpression="attribute_exists(short_id)",
            ExpressionAttributeValues={":zero": 0, ":one": 1, ":now": now},
            ReturnValues="ALL_NEW",
        )
    except ClientError as err:
        if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return respond(404, {"error": "Short link not found"})
        print(f"DynamoDB error: {err}")
        return respond(500, {"error": "Internal server error"})

    return {
        "statusCode": 302,
        "headers": {"Location": result["Attributes"]["original_url"]},
        "body": "",
    }
