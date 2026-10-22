# API Reference

Base URL: `https://rdch2zylwh.execute-api.ap-south-1.amazonaws.com`

| Method | Route | Lambda | Purpose |
|---|---|---|---|
| POST | `/shorten` | `shorten-url` | Create a short link |
| GET | `/{short_id}` | `redirect-url` | Redirect to the original URL and count a click |
| GET | `/stats/{short_id}` | `get-stats` | Return click statistics for a link |

## POST /shorten

**Request**

```json
{"url": "https://example.com"}
```

**Responses**

| Status | Body | When |
|---|---|---|
| 201 | `{"short_id": "7HWLp3", "original_url": "https://example.com", "short_url": "https://.../7HWLp3"}` | Link created |
| 400 | `{"error": "Request body must be valid JSON"}` | Body is not valid JSON |
| 400 | `{"error": "Request body must be a JSON object with a url field"}` | Body is JSON but not an object |
| 400 | `{"error": "Provide a valid http or https URL (max 2048 characters)"}` | URL is empty, not http/https, has no host, or is too long |
| 500 | `{"error": "Could not generate a unique ID, please retry"}` | 5 ID collisions in a row (very rare) |

## GET /{short_id}

**Responses**

| Status | Body | When |
|---|---|---|
| 302 | empty, with a `Location` header | Link found; click count increased |
| 400 | `{"error": "Missing short ID"}` | No ID in the path |
| 404 | `{"error": "Short link not found"}` | ID unknown or not 6 letters/digits |
| 500 | `{"error": "Internal server error"}` | DynamoDB failure |

## GET /stats/{short_id}

**Responses**

| Status | Body | When |
|---|---|---|
| 200 | `{"short_id": "...", "original_url": "...", "clicks": 2, "created_at": "...", "last_accessed": "..."}` | Link found (`last_accessed` is `null` if never opened) |
| 400 | `{"error": "Missing short ID"}` | No ID in the path |
| 404 | `{"error": "Short link not found"}` | ID unknown |
| 500 | `{"error": "Internal server error"}` | DynamoDB failure |

## Other behavior

- CORS is enabled for all origins (`*`) with methods GET, POST, OPTIONS.
- Default stage throttling: 20 requests/second, burst 40.
- Under a sudden burst above the account's Lambda concurrency limit (about 10), requests can return 503.
