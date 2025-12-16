"""Summary generation for benchmark results."""

from typing import List, Dict, Any, Optional
import statistics


def generate_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics from benchmark results.
    
    Args:
        results: List of result dictionaries
        
    Returns:
        Summary dictionary with statistics
    """
    if not results:
        return {
            'total_requests': 0,
            'ok_requests': 0,
            'client_latency_mean': None,
            'client_latency_p50': None,
            'client_latency_p95': None,
            'api_latency_mean': None,
            'api_latency_p50': None,
            'api_latency_p95': None,
            'total_reference_baseline_cost_usd': None,
            'total_an1_cost_usd': None,
            'total_savings_usd': None,
            'savings_percentage': None
        }
    
    total_requests = len(results)
    ok_results = [r for r in results if r.get('ok', False)]
    ok_requests = len(ok_results)
    
    # Wall-clock latency statistics (primary)
    client_latencies = []
    for r in ok_results:
        latency = r.get('client_elapsed_ms')
        if latency is not None and latency != '':
            try:
                client_latencies.append(float(latency))
            except (ValueError, TypeError):
                pass
    
    client_latency_mean = statistics.mean(client_latencies) if client_latencies else None
    client_latency_p50 = statistics.median(client_latencies) if client_latencies else None
    client_latency_p95 = None
    if client_latencies:
        sorted_latencies = sorted(client_latencies)
        p95_index = int(len(sorted_latencies) * 0.95)
        client_latency_p95 = sorted_latencies[p95_index] if p95_index < len(sorted_latencies) else sorted_latencies[-1]
    
    # API-reported latency statistics (for comparison)
    api_latencies = []
    for r in ok_results:
        latency = r.get('api_latency_ms')
        if latency is not None and latency != '':
            try:
                api_latencies.append(float(latency))
            except (ValueError, TypeError):
                pass
    
    api_latency_mean = statistics.mean(api_latencies) if api_latencies else None
    api_latency_p50 = statistics.median(api_latencies) if api_latencies else None
    api_latency_p95 = None
    if api_latencies:
        sorted_latencies = sorted(api_latencies)
        p95_index = int(len(sorted_latencies) * 0.95)
        api_latency_p95 = sorted_latencies[p95_index] if p95_index < len(sorted_latencies) else sorted_latencies[-1]
    
    # Cost statistics
    reference_costs = []
    an1_costs = []
    savings = []
    
    for r in ok_results:
        ref_cost = r.get('reference_baseline_cost_usd')
        an1_cost = r.get('an1_cost_usd')
        saving = r.get('savings_usd')
        
        if ref_cost and ref_cost != '':
            try:
                reference_costs.append(float(ref_cost))
            except (ValueError, TypeError):
                pass
        
        if an1_cost and an1_cost != '':
            try:
                an1_costs.append(float(an1_cost))
            except (ValueError, TypeError):
                pass
        
        if saving and saving != '':
            try:
                savings.append(float(saving))
            except (ValueError, TypeError):
                pass
    
    total_reference_baseline_cost_usd = sum(reference_costs) if reference_costs else None
    total_an1_cost_usd = sum(an1_costs) if an1_costs else None
    total_savings_usd = sum(savings) if savings else None
    
    # Calculate savings percentage
    savings_percentage = None
    if total_reference_baseline_cost_usd and total_reference_baseline_cost_usd > 0:
        if total_savings_usd is not None:
            savings_percentage = (total_savings_usd / total_reference_baseline_cost_usd) * 100
        elif total_an1_cost_usd is not None:
            savings_percentage = ((total_reference_baseline_cost_usd - total_an1_cost_usd) / total_reference_baseline_cost_usd) * 100
    
    return {
        'total_requests': total_requests,
        'ok_requests': ok_requests,
        'client_latency_mean': client_latency_mean,
        'client_latency_p50': client_latency_p50,
        'client_latency_p95': client_latency_p95,
        'api_latency_mean': api_latency_mean,
        'api_latency_p50': api_latency_p50,
        'api_latency_p95': api_latency_p95,
        'total_reference_baseline_cost_usd': total_reference_baseline_cost_usd,
        'total_an1_cost_usd': total_an1_cost_usd,
        'total_savings_usd': total_savings_usd,
        'savings_percentage': savings_percentage
    }
