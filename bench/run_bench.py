"""Main benchmark runner for AN1 API."""

import os
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional

from .http_client import create_client


def load_inputs(data_file: str) -> List[Dict[str, Any]]:
    """Load input data from JSON file."""
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_metrics(response: Dict[str, Any], expected_mode: Optional[str]) -> Dict[str, Any]:
    """Extract metrics from API response."""
    api_mode = response.get('mode')
    
    # Validate mode if expected_mode is set
    if expected_mode and expected_mode != 'unknown' and api_mode:
        if api_mode != expected_mode:
            print(f"Warning: Expected mode '{expected_mode}' but API returned '{api_mode}'")
    
    return {
        'mode': api_mode or expected_mode or 'unknown',
        'reference_baseline_cost_usd': response.get('reference_baseline_cost_usd'),
        'an1_cost_usd': response.get('an1_cost_usd'),
        'savings_usd': response.get('savings_usd'),
    }


def run_benchmark():
    """Run the benchmark and write results."""
    # Configuration
    base_url = os.getenv('AN1_API_URL') or os.getenv('AN1_BENCH_URL')
    if not base_url:
        print("Error: AN1_API_URL environment variable is required")
        return 1
    
    print(f"Calling: {base_url}")
    
    expected_mode = os.getenv('AN1_EXPECTED_MODE')  # Optional, no default
    num_requests = os.getenv('AN1_NUM_REQUESTS')
    
    # Generate output file label
    output_label = expected_mode if expected_mode else 'run'
    
    # Load inputs
    data_file = Path(__file__).parent.parent / 'data' / 'sessions_v1.json'
    inputs = load_inputs(data_file)
    
    # Limit number of requests if specified
    if num_requests:
        inputs = inputs[:int(num_requests)]
    
    # Create client
    client = create_client()
    
    # Create output directory
    out_dir = Path(__file__).parent.parent / 'out'
    out_dir.mkdir(exist_ok=True)
    
    # Prepare results
    results = []
    
    # Run benchmark
    for input_data in inputs:
        input_id = input_data['id']
        input_text = input_data['input']
        
        # Make API call (z vector generated automatically from text)
        result = client.call(input_text)
        
        # Extract metrics
        response_data = result.get('response', {})
        metrics = extract_metrics(response_data, expected_mode)
        
        # Record result with both latency measurements
        row = {
            'input_id': input_id,
            'ok': result['ok'],
            'status_code': result['status_code'],
            'api_latency_ms': round(result['api_latency_ms'], 2) if result.get('api_latency_ms') is not None else '',
            'client_elapsed_ms': round(result['client_elapsed_ms'], 2),
            'mode': metrics['mode'],
            'reference_baseline_cost_usd': metrics['reference_baseline_cost_usd'] or '',
            'an1_cost_usd': metrics['an1_cost_usd'] or '',
            'savings_usd': metrics['savings_usd'] or '',
            'error': result['error'] or ''
        }
        results.append(row)
    
    # Write CSV results
    csv_file = out_dir / f'results_{output_label}.csv'
    if results:
        fieldnames = [
            'input_id', 'ok', 'status_code', 'api_latency_ms', 'client_elapsed_ms', 'mode',
            'reference_baseline_cost_usd', 'an1_cost_usd', 'savings_usd', 'error'
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Results written to {csv_file}")
    
    # Generate summary
    from .summarize import generate_summary
    summary = generate_summary(results)
    
    summary_file = out_dir / f'summary_{output_label}.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary written to {summary_file}")
    print(f"\nSummary:")
    print(f"  Total requests: {summary['total_requests']}")
    print(f"  Successful requests: {summary['ok_requests']}")
    if summary['client_latency_mean']:
        print(f"  Mean latency (wall-clock): {summary['client_latency_mean']:.2f} ms")
    if summary['client_latency_p50']:
        print(f"  P50 latency (wall-clock): {summary['client_latency_p50']:.2f} ms")
    if summary['client_latency_p95']:
        print(f"  P95 latency (wall-clock): {summary['client_latency_p95']:.2f} ms")
    if summary['total_reference_baseline_cost_usd']:
        print(f"  Total reference baseline cost: ${summary['total_reference_baseline_cost_usd']:.6f}")
    if summary['total_an1_cost_usd']:
        print(f"  Total AN1 cost: ${summary['total_an1_cost_usd']:.6f}")
    if summary['total_savings_usd']:
        print(f"  Total savings: ${summary['total_savings_usd']:.6f}")
    if summary['savings_percentage']:
        print(f"  Savings percentage: {summary['savings_percentage']:.1f}%")
    
    return 0


if __name__ == '__main__':
    exit(run_benchmark())
