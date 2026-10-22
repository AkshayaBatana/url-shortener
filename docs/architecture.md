# Architecture

```mermaid
flowchart LR
    User([User / Browser])
    S3[S3 Static Website<br/>index.html, app.js]
    APIGW[API Gateway HTTP API<br/>url-shortener-api]
    L1[Lambda<br/>shorten-url]
    L2[Lambda<br/>redirect-url]
    L3[Lambda<br/>get-stats]
    DDB[(DynamoDB<br/>url-shortener-table)]
    CW[CloudWatch Logs<br/>14-day retention]

    User -->|loads page| S3
    User -->|POST /shorten| APIGW
    User -->|GET /short_id| APIGW
    User -->|GET /stats/short_id| APIGW
    APIGW --> L1
    APIGW --> L2
    APIGW --> L3
    L1 -->|PutItem| DDB
    L2 -->|UpdateItem| DDB
    L3 -->|GetItem| DDB
    L1 -.-> CW
    L2 -.-> CW
    L3 -.-> CW
```

## Request flow

1. The browser loads the page from S3 and calls `POST /shorten`.
2. `shorten-url` validates the URL, creates a 6-character ID and stores it in DynamoDB.
3. Visiting `GET /{short_id}` runs `redirect-url`, which counts the click and returns a 302 redirect.
4. `GET /stats/{short_id}` runs `get-stats`, which returns the URL, click count and timestamps.
