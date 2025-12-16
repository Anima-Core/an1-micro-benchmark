# AN1 Micro-Benchmark

A minimal, reproducible benchmarking harness for measuring latency and cost deltas when calling the AN1 API endpoint. This tool treats AN1 as a black box and makes no assumptions about how costs or modes are computed.

## Overview

This benchmark suite executes a series of classification requests against the AN1 API and captures:

- Request latency (mean, P50, P95)
- Cost metrics (reference baseline cost, AN1 cost, savings)
- Success/failure rates
- Error details

**Important**: This is a micro-benchmark designed to measure specific deltas between different API configurations. Results should not be interpreted as generalized performance claims.

**Safety / Disclosure**: This benchmark reports externally observable metrics only. It intentionally omits implementation details and internal controls.

## Requirements

- Python 3.8 or higher
- `requests` library

## Installation

```bash
pip install -r requirements.txt
```

Or using pip with pyproject.toml:

```bash
pip install .
```

## Configuration

Set the following environment variables:

### Required

- `AN1_API_URL`: Base URL for the AN1 API endpoint (e.g., `https://mydomain.vercel.app/api/an1-turbo`)

### Optional

- `AN1_API_KEY`: Bearer token for API authentication (if required)
- `AN1_EXPECTED_MODE`: Optional label for output files and mode validation (if set, validates API response mode matches)
- `AN1_NUM_REQUESTS`: Limit number of requests to process (default: all inputs)
- `AN1_TIMEOUT_SECONDS`: Request timeout in seconds (default: 120)

## Usage

### Single Run

```bash
AN1_API_URL=https://your-domain.vercel.app/api/an1-turbo \
python -m bench.run_bench
```

Optionally label the run and validate mode:

```bash
AN1_API_URL=https://your-domain.vercel.app/api/an1-turbo \
AN1_EXPECTED_MODE=baseline_only \
python -m bench.run_bench
```

### Run Both Modes

```bash
AN1_API_URL=https://your-domain.vercel.app/api/an1-turbo \
bash scripts/run_all.sh
```

## API Contract

### Request Format

```json
{
  "task": "classification",
  "input": "Sample input text for benchmark"
}
```

### Response Format

The API returns a JSON object with the following structure:

```json
{
  "ok": true,
  "mode": "infer",
  "latency_ms": 50,
  "reference_baseline_cost_usd": 0.040,
  "an1_cost_usd": 0.015,
  "savings_usd": 0.018
}
```

The benchmark extracts and aggregates these metrics without making any assumptions about how they are computed.

## Outputs

Results are written to the `out/` directory (gitignored):

- `out/results_<mode>.csv`: Detailed per-request metrics
- `out/summary_<mode>.json`: Aggregated statistics

### CSV Columns

- `input_id`: Input identifier
- `ok`: Whether request succeeded (boolean)
- `status_code`: HTTP status code
- `api_latency_ms`: Server-reported processing time in milliseconds (may exclude network and queueing)
- `client_elapsed_ms`: Wall-clock elapsed time in milliseconds (includes network and end-to-end overhead)
- `mode`: Mode identifier from API response
- `reference_baseline_cost_usd`: Reference baseline cost in USD
- `an1_cost_usd`: AN1 cost in USD
- `savings_usd`: Savings amount in USD
- `error`: Error message (if any)

### Summary JSON

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

**Note**: Latency statistics use wall-clock elapsed time (`client_elapsed_ms`) as the primary metric to ensure independent verification. Server-reported latency (`api_latency_ms`) is also recorded for comparison.

## Dataset

The benchmark uses `data/sessions_v1.json`, which contains 20 classification input examples with generic, non-sensitive text samples.

## Mechanism Intentionally Withheld

The internal mechanisms by which different API configurations produce different performance characteristics are proprietary and subject to non-disclosure agreements. This benchmark harness is designed to measure observable deltas only and does not reveal, document, or explain any internal implementation details, algorithms, or architectural decisions.

To generate different benchmark runs (e.g., `baseline_only` vs `active`), configure the appropriate environment variables on your API server. The benchmark harness itself makes no assumptions about how these configurations differ internally.

## Error Handling

The benchmark includes automatic retry logic with exponential backoff for transient failures (HTTP 429, 503, timeouts, connection errors). Maximum retries: 3.

All errors are recorded in the results CSV and do not cause the benchmark to crash mid-run.

## License

MIT License - see LICENSE file for details.
