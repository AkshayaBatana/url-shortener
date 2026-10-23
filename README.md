# Serverless URL Shortener

A URL shortener built on AWS serverless services: an S3 static frontend, an API Gateway HTTP API, three Python Lambda functions and a DynamoDB table. Region: ap-south-1 (Mumbai).

## Features

- Shorten any http/https URL to a 6-character link
- Redirect with click counting
- Statistics endpoint (original URL, clicks, created and last-accessed time)
- Input validation and JSON error responses
- Least-privilege IAM roles, API throttling and 14-day log retention

## Architecture

| Component | Service |
|---|---|
| Frontend | S3 static website (`frontend/`) |
| API | API Gateway HTTP API `url-shortener-api` |
| Backend | Lambda `shorten-url`, `redirect-url`, `get-stats` (`backend/`) |
| Database | DynamoDB `url-shortener-table` (on-demand capacity) |

Diagram and request flow: ![docs/architecture.md](docs/architecture.md)

## API

| Method | Route | Purpose |
|---|---|---|
| POST | `/shorten` | Create a short link |
| GET | `/{short_id}` | Redirect to the original URL and count a click |
| GET | `/stats/{short_id}` | Get click statistics |

Request and response details: ![docs/api-reference.md](docs/api-reference.md)

Example:

```bash
curl -X POST $URL/shorten -H "Content-Type: application/json" -d '{"url":"https://example.com"}'
```

## Screenshots

### Frontend

![Frontend](docs/screenshot-frontend.png)

### API Gateway routes

`POST /shorten`

![POST /shorten route](docs/url-shortner-api-shorten-route.png)

`GET /{short_id}`

![GET /{short_id} route](docs/url-shortner-api-short-id-route.png)

`GET /stats/{short_id}`

![GET /stats/{short_id} route](docs/url-shortner-api-stats-route.png)

### DynamoDB table

![DynamoDB table](docs/screenshot-dynamodb.png)

## Testing

Functional, validation and load test results: [docs/test-report.md](docs/test-report.md)

## Repository layout

```
backend/    Lambda source code (shorten, redirect, stats)
frontend/   index.html and app.js
docs/       architecture, API reference, test report, screenshots
infra/      infrastructure notes
```
