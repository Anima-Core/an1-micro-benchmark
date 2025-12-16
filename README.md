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

---

## Installation

Using `pip`:

```bash
pip install -r requirements.txt
```

Or using pyproject.toml:

```bash
pip install .
```

---

## Configuration

Set the following environment variables before running the benchmark.

### Required

- **`AN1_API_URL`**  
  Base URL for the AN1 API endpoint  
  (e.g. `https://www.animacore.ai/api/an1-turbo`)

- **`AN1_API_KEY`**  
  Bearer token for API authentication (required for deployed endpoints)

### Optional

- **`AN1_EXPECTED_MODE`**  
  Optional label for output files and mode validation  
  (if set, the benchmark warns if the API response mode does not match)

- **`AN1_NUM_REQUESTS`**  
  Limit the number of requests processed  
  (default: all inputs)

- **`AN1_TIMEOUT_SECONDS`**  
  Request timeout in seconds  
  (default: 120)

---

## Usage

### Setup (PowerShell)

```powershell
$env:AN1_API_URL="https://www.animacore.ai/api/an1-turbo"
$env:AN1_API_KEY="YOUR_API_KEY"
```

### Run Benchmark

```powershell
python -m bench.run_bench
```

### Labeled Run (optional)

```powershell
$env:AN1_EXPECTED_MODE="baseline_only"
python -m bench.run_bench
```

### Run Multiple Configurations

```powershell
bash scripts/run_all.sh
```

**Note:** The benchmark automatically generates deterministic z vectors from text inputs. You do not need to create z vectors manually.

---

## API Contract

### Request Format

The benchmark uses `infer_z` mode by default for reproducibility and stability:

```json
{
  "mode": "infer_z",
  "z": [256 floating point values]
}
```

The harness automatically converts text samples from the dataset into deterministic 256-float z vectors using a hash-based approach. This ensures:
- Deterministic results across runs
- No external ML dependencies
- Stable, reproducible benchmark inputs

**Optional text mode** (may be unavailable in some deployments):

```json
{
  "mode": "infer_text",
  "text": "example input"
}
```

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

## Sanity Check

Test the API endpoint with a minimal request (PowerShell):

```powershell
# Create request file with 256 zeros
$z = [0.0] * 256
$payload = @{
    mode = "infer_z"
    z = $z
} | ConvertTo-Json -Compress

$payload | Out-File -Encoding utf8 request.json

# Send request
curl.exe -i -sS -L -X POST "$env:AN1_API_URL" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $env:AN1_API_KEY" `
  --data-binary "@request.json"
```

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

## Mechanism Intentionally Withheld

The internal mechanisms by which different API configurations produce different performance characteristics are proprietary and subject to non-disclosure agreements.

This benchmark harness is designed to measure observable deltas only and does not reveal, document, or explain any internal implementation details, algorithms, heuristics, or architectural decisions.

To generate different benchmark runs (e.g. `baseline_only` vs `active`), configure the appropriate environment variables on the API server. The benchmark harness itself makes no assumptions about how these configurations differ internally.

---

## Error Handling

The benchmark includes automatic retry logic with exponential backoff for transient failures:

- HTTP 429
- HTTP 503
- timeouts
- connection errors

**Maximum retries:** 3

All errors are recorded in the results CSV and do not cause the benchmark to crash mid-run.

---

## License

MIT License. See the LICENSE file for details.
