"""Helper functions for labor supply response calculations."""
import numpy as np


def pos(x):
    """Clip negative values to zero.
    
    Args:
        x: Array or scalar values
        
    Returns:
        Array with negative values set to zero
    """
    return np.where(x <= 0, 0.0, x)


def safe_share(numerator, denominator):
    """Safely calculate a share with division by zero protection.
    
    Args:
        numerator: Array or scalar numerator values
        denominator: Array or scalar denominator values
        
    Returns:
        Array with safe division, returning 0 when denominator <= 0
    """
    return np.where(denominator > 0, numerator / denominator, 0.0)