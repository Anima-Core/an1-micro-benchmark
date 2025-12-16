#!/bin/bash
# Run benchmark in both modes

set -e

if [ -z "$AN1_API_URL" ]; then
    echo "Error: AN1_API_URL environment variable is required"
    exit 1
fi

echo "Running baseline_only benchmark..."
AN1_EXPECTED_MODE=baseline_only python -m bench.run_bench

echo ""
echo "Running active benchmark..."
AN1_EXPECTED_MODE=active python -m bench.run_bench

echo ""
echo "Benchmark runs complete. Check out/ directory for results."

