"""HTTP client with retry logic for AN1 API calls."""

import os
import time
import requests
from typing import Optional, Dict, Any


class AN1Client:
    """Client for making requests to AN1 API endpoint."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 120):
        """
        Initialize AN1 client.
        
        Args:
            base_url: Base URL for AN1 API (e.g., https://example.com/api/an1-turbo)
            api_key: Optional API key for Bearer authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
        
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def call(self, task: str, input_text: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Make a request to AN1 API with retry logic.
        
        Args:
            task: Task type (e.g., "classification")
            input_text: Input text for the task
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict with 'ok', 'status_code', 'latency_ms', 'response', 'error'
        """
        payload = {
            'task': task,
            'input': input_text
        }
        start_time = time.time()
        
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    self.base_url,
                    json=payload,
                    timeout=self.timeout
                )
                
                latency_ms = (time.time() - start_time) * 1000
                
                if response.status_code in (429, 503):
                    # Transient error, retry with exponential backoff
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        time.sleep(wait_time)
                        continue
                
                response.raise_for_status()
                response_data = response.json() if response.content else {}
                
                # Record both API-reported and wall-clock latency
                client_elapsed_ms = (time.time() - start_time) * 1000
                api_latency_ms = response_data.get('latency_ms')
                
                result = {
                    'ok': True,
                    'status_code': response.status_code,
                    'api_latency_ms': api_latency_ms,
                    'client_elapsed_ms': client_elapsed_ms,
                    'response': response_data,
                    'error': None
                }
                
                return result
                
            except requests.exceptions.Timeout:
                client_elapsed_ms = (time.time() - start_time) * 1000
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                
                return {
                    'ok': False,
                    'status_code': 0,
                    'api_latency_ms': None,
                    'client_elapsed_ms': client_elapsed_ms,
                    'response': {},
                    'error': 'Timeout'
                }
                
            except requests.exceptions.RequestException as e:
                client_elapsed_ms = (time.time() - start_time) * 1000
                if attempt < max_retries - 1 and isinstance(e, requests.exceptions.ConnectionError):
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                
                error_msg = str(e)
                if len(error_msg) > 100:
                    error_msg = error_msg[:97] + '...'
                
                return {
                    'ok': False,
                    'status_code': getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0,
                    'api_latency_ms': None,
                    'client_elapsed_ms': client_elapsed_ms,
                    'response': {},
                    'error': error_msg
                }
        
        # Should not reach here, but handle gracefully
        return {
            'ok': False,
            'status_code': 0,
            'api_latency_ms': None,
            'client_elapsed_ms': (time.time() - start_time) * 1000,
            'response': {},
            'error': 'Max retries exceeded'
        }


def create_client() -> AN1Client:
    """Create AN1 client from environment variables."""
    base_url = os.getenv('AN1_API_URL') or os.getenv('AN1_BENCH_URL')
    if not base_url:
        raise ValueError("AN1_API_URL environment variable is required")
    
    api_key = os.getenv('AN1_API_KEY')
    timeout = int(os.getenv('AN1_TIMEOUT_SECONDS', '120'))
    
    return AN1Client(base_url, api_key, timeout)

