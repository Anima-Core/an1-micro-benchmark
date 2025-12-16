# AN1 Micro-Benchmark

A minimal, reproducible benchmarking harness for measuring **latency and cost deltas** when calling the AN1 API endpoint.  
This tool treats AN1 strictly as a **black box** and makes no assumptions about how costs, modes, or behaviors are computed internally.

---

## Overview

This benchmark suite executes a fixed set of classification requests against the AN1 API and captures **externally observable metrics** only:

- Request latency (mean, P50, P95)
- Cost metrics (reference baseline cost, AN1 cost, savings)
- Success and failure rates
- Error details for unsuccessful requests

**Important:**  
This is a **micro-benchmark** designed to measure *specific deltas under controlled conditions*.  
Results should **not** be interpreted as generalized performance claims.

**Safety / Disclosure:**  
This benchmark reports externally observable metrics only. It intentionally omits implementation details, internal controls, algorithms, and architectural decisions.

---

## Requirements

- Python 3.8 or higher
- `requests` library
- Windows PowerShell (for sanity check script)
- `curl.exe` (included with Windows 10+)

---

## Quick Start (PowerShell)

### 1. Install Dependencies

```powershell
# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 2. Set Environment Variables

```powershell
$env:AN1_API_URL="https://www.animacore.ai/api/an1-turbo"
$env:AN1_API_KEY="YOUR_API_KEY"
```

### 3. Run Sanity Check

```powershell
.\scripts\sanity_check.ps1
```

This verifies your API endpoint is accessible and accepts `infer_z` requests before running the full benchmark.

### 4. Run Benchmark

```powershell
python -m bench.run_bench
```

### 5. View Summary

Results are written to `out/summary_run.json`. You can also view the CSV file `out/results_run.csv` for per-request details.

---

## Configuration

### Required Environment Variables

- **`AN1_API_URL`**  
  Base URL for the AN1 API endpoint  
  Example: `https://www.animacore.ai/api/an1-turbo`

- **`AN1_API_KEY`**  
  Bearer token for API authentication  
  **Required** for all deployed endpoints

### Optional Environment Variables

- **`AN1_EXPECTED_MODE`**  
  Optional label for output files and mode validation  
  If set, the benchmark warns if the API response mode does not match

- **`AN1_NUM_REQUESTS`**  
  Limit the number of requests processed  
  Default: all inputs (20)

- **`AN1_TIMEOUT_SECONDS`**  
  Request timeout in seconds  
  Default: 120

---

## API Contract

### Request Format

The benchmark uses `infer_z` mode exclusively. This mode is supported in all backend configurations and provides deterministic, reproducible results.

**Request payload:**

```json
{
  "mode": "infer_z",
  "z": [256 floating point values]
}
```

**Requirements:**
- `z` must be exactly 256 floating point numbers
- Values are typically in range [-1.0, 1.0]
- The harness automatically generates deterministic z vectors from text inputs

**Note:** The API may also support `infer_text` mode in some deployments, but this benchmark uses `infer_z` for consistency and reproducibility.

### Response Format

The API returns a JSON object with the following structure:

```json
{
  "ok": true,
  "mode": "infer",
  "backend": "local",
  "version": "0.1.2",
  "latency_ms": 50,
  "reference_baseline_cost_usd": 0.040,
  "an1_cost_usd": 0.015,
  "savings_usd": 0.018
}
```

The benchmark extracts and aggregates these values without making any assumptions about how they are produced.

---

## Outputs

Results are written to the `out/` directory (gitignored).

### Files

- **`out/results_<mode>.csv`**  
  Detailed per-request metrics

- **`out/summary_<mode>.json`**  
  Aggregated statistics

### CSV Columns

- `input_id` — input identifier
- `ok` — whether the request succeeded
- `status_code` — HTTP status code
- `api_latency_ms` — server-reported processing time (may exclude network and queueing)
- `client_elapsed_ms` — wall-clock elapsed time (includes network and end-to-end overhead)
- `mode` — mode identifier returned by the API
- `reference_baseline_cost_usd` — reference baseline cost in USD
- `an1_cost_usd` — AN1 cost in USD
- `savings_usd` — savings amount in USD
- `error` — error message (if any)

### Summary JSON Example

```json
{
  "total_requests": 20,
  "ok_requests": 20,
  "client_latency_mean": 45.2,
  "client_latency_p50": 48.0,
  "client_latency_p95": 52.3,
  "api_latency_mean": 44.8,
  "api_latency_p50": 47.5,
  "api_latency_p95": 51.9,
  "total_reference_baseline_cost_usd": 0.800,
  "total_an1_cost_usd": 0.300,
  "total_savings_usd": 0.500,
  "savings_percentage": 62.5
}
```

**Note:**  
Wall-clock elapsed time (`client_elapsed_ms`) is used as the primary latency metric to ensure independent verification.  
Server-reported latency (`api_latency_ms`) is recorded for comparison only.

---

## Dataset

The benchmark uses `data/sessions_v1.json`, which contains 20 text input examples with generic, non-sensitive samples. The harness automatically converts these text inputs to deterministic 256-float z vectors using a hash-based generator.

---

## Troubleshooting

### HTTP 400: Invalid z dimension

**Error message:** `"z dimension must be exactly 256"` or similar

**Cause:** The z vector length is not exactly 256.

**Solution:** This should never occur with the benchmark harness, as it automatically generates 256-element vectors. If you see this error:
1. Check that you're using the latest version of the benchmark
2. Verify the dataset file `data/sessions_v1.json` is not corrupted
3. Report this as a bug (the harness includes assertions to catch this)

### HTTP 401 / 403: Authentication errors

**Error message:** `"Unauthorized"` or `"Forbidden"`

**Cause:** Missing or invalid API key.

**Solution:**
1. Verify `AN1_API_KEY` is set: `echo $env:AN1_API_KEY`
2. Ensure the key is correct and has not expired
3. Check that the key includes the full token (no truncation)
4. Verify the Authorization header format: `Bearer <key>`

### HTTP 503: Kill switch enabled

**Error message:** `"Service unavailable"` or `"Kill switch enabled"`

**Cause:** The API server has a kill switch enabled, typically after environment variable changes.

**Solution:**
1. The API deployment needs to be redeployed after environment variable changes
2. Contact the API administrator to redeploy the service
3. Wait for the deployment to complete before retrying

### Connection errors / Timeouts

**Error message:** Connection refused, timeout, or network errors

**Cause:** Network issues or API endpoint is down.

**Solution:**
1. Verify `AN1_API_URL` is correct and accessible
2. Check your network connection
3. Try the sanity check script: `.\scripts\sanity_check.ps1`
4. Increase timeout if needed: `$env:AN1_TIMEOUT_SECONDS="300"`

### z vector length assertion error

**Error message:** `"Generated z vector has length X, expected exactly 256"`

**Cause:** Bug in the z vector generator (should never occur).

**Solution:** Report this as a bug. The harness includes assertions to catch this condition.

---

## Mechanism Intentionally Withheld

The internal mechanisms by which different API configurations produce different performance characteristics are proprietary and subject to non-disclosure agreements.

This benchmark harness is designed to measure observable deltas only and does not reveal, document, or explain any internal implementation details, algorithms, heuristics, or architectural decisions.

To generate different benchmark runs (e.g. `baseline_only` vs `active`), configure the appropriate environment variables on the API server. The benchmark harness itself makes no assumptions about how these configurations differ internally.

---

## Error Handling

The benchmark includes automatic retry logic with exponential backoff for transient failures:

- HTTP 429 (rate limiting)
- HTTP 503 (service unavailable)
- Timeouts
- Connection errors

**Maximum retries:** 3

All errors are recorded in the results CSV and do not cause the benchmark to crash mid-run.

---

## License

MIT License. See the LICENSE file for details.
