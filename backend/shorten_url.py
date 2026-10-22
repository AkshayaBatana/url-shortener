import json
import os
import secrets
import string
from datetime import datetime, timezone
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])

ALPHABET = string.ascii_letters + string.digits
ID_LENGTH = 6
MAX_URL_LENGTH = 2048
MAX_ATTEMPTS = 5


def respond(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }


def is_valid_url(url):
    if not isinstance(url, str) or not url or len(url) > MAX_URL_LENGTH:
        return False
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def new_id():
    return "".join(secrets.choice(ALPHABET) for _ in range(ID_LENGTH))


def lambda_handler(event, context):
    # API Gateway sends the body as a JSON string; the console test
    # event can also pass {"url": "..."} directly.
    try:
        body = event.get("body", event)
        data = json.loads(body) if isinstance(body, str) else body
    except json.JSONDecodeError:
        return respond(400, {"error": "Request body must be valid JSON"})

    if not isinstance(data, dict):
        return respond(400, {"error": "Request body must be a JSON object with a url field"})

    url = data.get("url", "")
    if not is_valid_url(url):
        return respond(400, {"error": "Provide a valid http or https URL (max 2048 characters)"})

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for _ in range(MAX_ATTEMPTS):
        short_id = new_id()
        try:
            table.put_item(
                Item={
                    "short_id": short_id,
                    "original_url": url,
                    "clicks": 0,
                    "created_at": now,
                },
                ConditionExpression="attribute_not_exists(short_id)",
            )
        except ClientError as err:
            if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
                continue  # collision: try another ID
            raise

        domain = (event.get("requestContext") or {}).get("domainName")
        result = {"short_id": short_id, "original_url": url}
        if domain:
            result["short_url"] = f"https://{domain}/{short_id}"
        return respond(201, result)

    return respond(500, {"error": "Could not generate a unique ID, please retry"})
