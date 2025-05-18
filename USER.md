# User Guide

This guide provides instructions on how to use the command-line interface (CLI) and the HTTP API for the Batch-on-Kafka system.

## Prerequisites

-   Docker and Docker Compose installed.
-   Access to a terminal or command prompt.
-   The `batch.cli` binary (this is built automatically when using Docker Compose).

## Running the System

The easiest way to run the API server, Kafka, and the worker is using Docker Compose:

```bash
# Build and start all services in detached mode
docker-compose up --build -d

# To view logs
docker-compose logs -f api worker

# To stop and remove containers, networks, volumes
docker-compose down -v
```

The API server will be available at `http://localhost:8000`.

**Note on Storage:** This implementation uses in-memory storage for models and job metadata. This means all data will be lost when the API server restarts. It is intended for demonstration purposes.

## Command-Line Interface (CLI)

A rich CLI is provided. Run commands using `batch.cli <command>` (or `./batchcli <command>` if built locally).

Ensure the API URL is set if the server is not running at the default `http://localhost:8000`:
```bash
export BATCH_API_URL=http://localhost:8000
```

### Model Commands

#### `model list`
Lists available models.

```bash
./batchcli model list
```
*(Sample output format TBD)*

#### `model describe <model>`
Shows details for a specific model.

```bash
./batchcli model describe <model_id>
```
*(Sample output format TBD)*

#### `model create <model_name> <path/to/schema.json>`
Creates a new model from a name and a JSON schema file.

```bash
./batchcli model create my_new_model ./schemas/new_model_schema.json
```
*(Sample output format TBD)*

#### `model update <model_id> <path/to/schema.json>`
Updates the schema for an existing model.

```bash
./batchcli model update <model_id> ./schemas/updated_schema.json
```
*(Sample output format TBD)*

#### `model delete <model_id>`
Deletes a model.

```bash
./batchcli model delete <model_id>
```
*(Sample output format TBD)*

### Job Commands

#### `job list`
Lists existing jobs with their status.

```bash
./batchcli job list
```

**Sample Output:**
```
JOB      MODEL       STATE           TOTAL   OK      ERRORS  PROGRESS                 WAITING  PROCESSSING
-------- ----------- --------------- ------- ------- ------- ------------------------ -------  -----------
a1b2c3d4 Fraud De..  SUCCESS           1,000   1,000       0 [#################] 100%   00:01        00:02
a2b3c4d5 Image Cl..  PARTIAL_SUCCESS  20,000  19,980      20 [###############X-]  99%   00:02        00:09
a3b4c5d6 Payment G.. RUNNING          50,000  30,500      12 [##########-------]  61%   00:03        00:40
a4b5c6d7 Anomaly D.. RUNNING           5,000   2,100       0 [#######----------]  42%   00:02        00:15
a5b6c7d8 model_123.. PENDING             100       0       0 [-----------------]   0%   00:04        00:00
a6b7c8d9 Alert Log.. PENDING           7,500       0       0 [-----------------]   0%   00:04        00:00
a7b8c9d0 Sentimen .. FAILED              800       0     800 [XXXXXXXXXXXXXXXXX]   0%   00:04        00:09
a8b9c0d1 Trend Pre.. CANCELLED         2,000     853       0 [########XXXXXXXXX]  46%   00:04        00:09
a9b0c1d2 Market Pr.. SUCCESS           3,200   3,200       0 [#################] 100%   00:02        00:03
```
*(Note: `PARTIAL_SUCCESS` state and timing fields are new requirements)*

#### `job create <model_id> <path/to/data.csv>`
Creates a new job for the given model and data file.

```bash
./batchcli job create model_123 data.csv
```

**Sample Output:**
```
job a5b6c7d8 created.
```

#### `job status <job_id>`
Shows the status of a specific job.

```bash
./batchcli job status a6b7c8d9
```

**Sample Output:**
```
JOB      MODEL       STATE           TOTAL   OK      ERRORS  PROGRESS                 WAITING  PROCESSSING
-------- ----------- --------------- ------- ------- ------- ------------------------ -------  -----------
a5b6c7d8 model_123.. PENDING             100       0       0 [-----------------]   0%   00:04        00:00
```
*(Note: Output format now matches `job list`)*

#### `job cancel <job_id>`
Cancels a job.

```bash
./batchcli job cancel a5b6c7d8
```

**Sample Output:**
```
job a5b6c7d8 cancelled
```

#### `job rejected <job_id>`
Displays rows that were rejected during processing for a specific job.

```bash
./batchcli job rejected a5b6c7d8
```

**Sample Output:**
```
ROW  EVENT_ID COLUMN      TYPE        ERROR               OBSERVED         MESSAGE
---- -------- ----------- ----------- ------------------- ---------------- ------------------------------------------------------------------------------------
1    1001abcd timestamp   TIMESTAMP   MISSING_COLUMN                       The required column 'timestamp' is missing. Please include a valid timestamp column.
2             event_id    STRING      MISSING_COLUMN                       The required column 'event_id' is missing. Each event must have a unique event_id.
3    1003cdef timestamp   TIMESTAMP   INVALID_TIMESTAMP   "yesterday"      The 'timestamp' value is invalid. Please provide a 32-bit Unix timestamp (integer).
4    1004def0 event_id    STRING      INVALID_EVENT_ID                     The 'event_id' value is invalid. Provide a non-empty string or integer identifier.
5    1005ef01 attr_float  FLOAT       NOT_A_FLOAT         "abc"            The value for 'attr_float' is not a float. Provide a numeric value (e.g. 3.14).
6    1006f012 attr_int    INTEGER     NOT_AN_INTEGER      "3.14"           The value for 'attr_int' is not an integer. Provide a whole number (e.g. 42).
7    1007abcd attr_bool   BOOLEAN     NOT_A_BOOLEAN       "maybe"          The value for 'attr_bool' is not a boolean. Use true, false, 1, or 0.
8    1008bcde attr_str    STRING      NOT_A_STRING        12345            The value for 'attr_str' is not a string. Provide a text value.
9    1009cdef attr_cat    CATEGORY    NOT_A_CATEGORY      "CA"             The value for 'attr_cat' is not a category. Provide a valid string category.
10   1010def0 attr_time   TIMESTAMP   NOT_A_TIMESTAMP     "2023-01-01"     The value for 'attr_time' is not a timestamp. Use a 32-bit Unix timestamp.
11   1011ef01 attr_vec    VECTOR      NOT_A_VECTOR        [1, "a", 3]      The value for 'attr_vec' is not a vector. Provide a list of numeric values.
12   1012f012 extra_col   STRING      EXTRA_COLUMN        "foo"            The column 'extra_col' is not in the schema. Remove or update your schema.
13   1013abcd attr_req    STRING      NULL_VALUE                           The column 'attr_req' is null or blank. Provide a valid value for this column.
14   1014bcde attr_x      FLOAT       UNSUPPORTED_TYPE    3.14             The column 'attr_x' uses unsupported type 'FLOAT'. Use a supported type.
```
*(Note: Requires backend storage and retrieval for rejected rows)*

#### `job reprocess <job_id>`
Triggers reprocessing of previously rejected rows for a job.
*(Assumption: This likely requires the user to have fixed the underlying data or schema)*

```bash
./batchcli reprocess a5b6c7d8
```

**Sample Output:**
```
Reprocessing job a5b6c7d8 created
```
*(Note: Requires a specific API endpoint and backend logic)*

### Utility Commands

#### `schema <path/to/data.csv>`
Detects and prints a suggested JSON schema based on the input CSV file.

```bash
./batchcli schema sample-data/sample.csv
```
*(Sample output format TBD. Requires schema detection logic, potentially standalone or via API)*

## HTTP API

The API provides programmatic access to the batch processing system. The default base URL is `http://localhost:8000`.

**Note:** The API uses a tenant system. Requests should include a tenant ID header. The specific header name (e.g., `X-Tenant-ID`) is determined by the `TENANT_HEADER` environment variable provided to the API server at startup. If the header is missing in a request, the API defaults to using the tenant ID `tenant_a`.

### Endpoints

#### `GET /models`

Lists all available models for the current tenant.

**Curl Example:**
```bash
# Using default tenant 'tenant_a'
curl http://localhost:8000/models

# Specifying a tenant
curl -H "X-Tenant-ID: my_tenant" http://localhost:8000/models
```

**Example Response (200 OK):**
```json
[
  {
    "model_id": "456a7890-b1cd-23ef-45gh-67890ijklmno",
    "tenant_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "name": "Sample Model",
    "schema": {
      "type": "object",
      "properties": {
        "id": { "type": "string" },
        "value": { "type": "integer" }
      },
      "required": ["id", "value"]
    },
    "created_at": "2023-03-15T12:00:00.000Z"
  }
]
```

#### `POST /models`

Creates a new model.

**Request Body (application/json):**
```json
{
  "name": "Sample Model",
  "schema": {
    "type": "object",
    "properties": {
      "id": { "type": "string" },
      "value": { "type": "integer" }
    },
    "required": ["id", "value"]
  }
}
```

**Curl Example:**
```bash
curl -X POST -H "Content-Type: application/json" -H "X-Tenant-ID: tenant_a" \
  -d '{ "name": "Sample Model", "schema": { "type": "object", "properties": { "id": { "type": "string" }, "value": { "type": "integer" } }, "required": ["id", "value"] } }' \
  http://localhost:8000/models
```

**Example Response (201 Created):**
```json
{
  "model_id": "456a7890-b1cd-23ef-45gh-67890ijklmno",
  "tenant_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "name": "Sample Model",
  "schema": {
    "type": "object",
    "properties": {
      "id": { "type": "string" },
      "value": { "type": "integer" }
    },
    "required": ["id", "value"]
  },
  "created_at": "2023-03-15T12:00:00.000Z"
}
```

#### `POST /jobs`

Creates a new processing job by uploading a data file.

**Request Body (multipart/form-data):**
-   `model_id`: The ID of the model to use (e.g., `456a7890-b1cd-23ef-45gh-67890ijklmno`).
-   `file`: The data file to process (e.g., `sample.csv`).

**Curl Example:**
```bash
curl -X POST -H "X-Tenant-ID: f47ac10b-58cc-4372-a567-0e02b2c3d479" \
  -F "model_id=456a7890-b1cd-23ef-45gh-67890ijklmno" \
  -F "file=@./sample-data/sample.csv" \
  http://localhost:8000/jobs
```

**Example Response (202 Accepted):**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "tenant_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "model_id": "456a7890-b1cd-23ef-45gh-67890ijklmno",
  "total": 0,
  "success": 0,
  "errors": 0,
  "state": "PENDING",
  "created_at": "2023-03-15T12:01:40.000Z",
  "updated_at": "2023-03-15T12:01:40.000Z"
}
```

#### `GET /jobs/:job_id`

Retrieves the status of a specific job.

**Curl Example:**
```bash
curl -H "X-Tenant-ID: f47ac10b-58cc-4372-a567-0e02b2c3d479" http://localhost:8000/jobs/123e4567-e89b-12d3-a456-426614174000
```

**Example Response (200 OK - Job Success):**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "tenant_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "model_id": "456a7890-b1cd-23ef-45gh-67890ijklmno",
  "total": 3,
  "success": 3,
  "errors": 0,
  "state": "SUCCESS", // Possible states: PENDING, RUNNING, SUCCESS, FAILED, CANCELLED
  "created_at": "2023-03-15T12:01:40.000Z",
  "updated_at": "2023-03-15T12:01:55.000Z"
}
```

**Example Response (200 OK - Job Pending):**
```json
{
  "job_id": "223e4567-e89b-12d3-a456-426614174001",
  "tenant_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "model_id": "456a7890-b1cd-23ef-45gh-67890ijklmno",
  "total": 0,
  "success": 0,
  "errors": 0,
  "state": "PENDING", // Possible states: PENDING, RUNNING, SUCCESS, FAILED, CANCELLED
  "created_at": "2023-03-15T12:02:00.000Z",
  "updated_at": "2023-03-15T12:02:00.000Z"
}
```

**Example Response (404 Not Found):**
```json
{
  "error": "not found"
}
```

#### `DELETE /jobs/:job_id`

Cancels a specific job.

**Curl Example:**
```bash
curl -X DELETE -H "X-Tenant-ID: f47ac10b-58cc-4372-a567-0e02b2c3d479" http://localhost:8000/jobs/123e4567-e89b-12d3-a456-426614174000
```

**Example Response (200 OK):**
```json
{
  "status": "cancelled"
}
```

**Example Response (404 Not Found):**
```json
{
  "error": "not found"
}
```
