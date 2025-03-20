"""
This module contains functions for calculus.
"""

def digit_sum(n: int) -> int:
    """Retorna la suma de las cifras del número n."""
    return n if n < 10 else (n // 10 + n % 10)
