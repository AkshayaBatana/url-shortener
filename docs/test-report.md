# Test Report

Date: 2026-10-22
Base URL: `https://rdch2zylwh.execute-api.ap-south-1.amazonaws.com`
Tools: curl from a Linux terminal, browser, phone, CloudWatch Monitor tab

## 1. Functional tests

| Test | Expected | Actual | Result |
|---|---|---|---|
| POST /shorten with valid URL | 201 + short_id | 201, short_id returned | Pass |
| GET /{short_id} | 302 + Location header | 302, Location: original URL | Pass |
| GET /stats/{short_id} | 200 + click count | 200, clicks increased after each redirect | Pass |
| Redirect opened on phone | Redirects to original URL | Redirected, click count +1 | Pass |
| Frontend on S3 website | Short link shown | Short link displayed and working | Pass |

## 2. Input validation and error handling

| Test | Expected | Actual | Result |
|---|---|---|---|
| Empty URL | 400 | 400 JSON error | Pass |
| `ftp://example.com` | 400 | 400 JSON error | Pass |
| `not a url` | 400 | 400 JSON error | Pass |
| `https://` (no host) | 400 | 400 JSON error | Pass |
| URL over 2048 characters | 400 | 400 JSON error | Pass |
| Invalid JSON body | 400 | 400 "Request body must be valid JSON" | Pass |
| JSON body that is not an object (`[1,2]`) | 400 | 400 "must be a JSON object" | Pass |
| Unknown ID (redirect) | 404 JSON | 404 `{"error": "Short link not found"}` | Pass |
| Unknown ID (stats) | 404 JSON | 404 `{"error": "Short link not found"}` | Pass |
| Malformed ID (`/abc`, `/ab%20cdef`) | 404 JSON | 404 JSON | Pass |
| Missing ID (`/stats/`) | 400 | 400 `{"error": "Missing short ID"}` | Pass |

## 3. Load and concurrency tests

| Test | Expected | Actual | Result |
|---|---|---|---|
| 20 requests sent simultaneously | all 2xx | 12 x 201, 8 x 503 | Fail (explained below) |
| 20 requests in 4 batches of 5 | all 2xx | 20 x 201 | Pass |
| Stats after burst | 200 + valid JSON | 200 | Pass |

**Finding.** In the simultaneous test, CloudWatch showed Lambda Throttles = 9, Concurrent executions = 10 and Errors = 0. The 503 responses were caused by the AWS account's Lambda concurrency limit (about 10), not by a code error or by API Gateway throttling (which would return 429). Every invocation that ran succeeded. Batches of 5 stay under the limit and all succeeded. Possible fix: request a concurrency quota increase through AWS Support.

## 4. Security and cost controls

| Check | Result |
|---|---|
| Each Lambda role has only a narrow inline DynamoDB policy on the single table (PutItem / GetItem+UpdateItem / GetItem) | Pass |
| No broad policies (e.g. AmazonDynamoDBFullAccess) attached | Pass |
| CloudWatch log retention set to 14 days on all three log groups | Pass |
| API Gateway default-stage throttling set to 20 rps, burst 40 | Pass |

## 5. Issues found and fixed

- Browser opened from `file://` failed with a CORS error; serving over http (localhost, then S3) fixed it.
- S3 bucket policy failed with "Policy has invalid resource" because the bucket name in the ARN was wrong; correcting it fixed it.
- `redirect-url`
