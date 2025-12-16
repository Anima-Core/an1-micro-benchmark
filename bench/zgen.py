"""Deterministic text-to-z vector generator for benchmark inputs."""

import hashlib
import random
from typing import List


def text_to_z(text: str, dim: int = 256) -> List[float]:
    """
    Generate a deterministic 256-float z vector from text input.
    
    Uses SHA256 hashing to seed a PRNG, ensuring the same text always
    produces the same z vector across runs and machines.
    
    Args:
        text: Input text string
        dim: Dimension of output vector (default: 256)
        
    Returns:
        List of exactly dim floats in range [-1.0, 1.0]
    """
    # Create deterministic seed from text hash
    text_bytes = text.encode('utf-8')
    hash_digest = hashlib.sha256(text_bytes).digest()
    seed = int.from_bytes(hash_digest[:8], 'big')
    
    # Use local random instance (not global) for thread safety
    rng = random.Random(seed)
    
    # Generate dim floats in range [-1.0, 1.0]
    z_vector = [rng.uniform(-1.0, 1.0) for _ in range(dim)]
    
    return z_vector

