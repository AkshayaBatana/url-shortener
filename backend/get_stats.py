import json
import os

import boto3
from botocore.exceptions import ClientError

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


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

    try:
        result = table.get_item(Key={"short_id": short_id})
    except ClientError as err:
        print(f"DynamoDB error: {err}")
        return respond(500, {"error": "Internal server error"})

    item = result.get("Item")
    if not item:
        return respond(404, {"error": "Short link not found"})

    return respond(200, {
        "short_id": item["short_id"],
        "original_url": item["original_url"],
        "clicks": int(item.get("clicks", 0)),  # DynamoDB returns numbers as Decimal
        "created_at": item.get("created_at"),
        "last_accessed": item.get("last_accessed"),
    })
