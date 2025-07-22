"""Test decile_rank() method with negatives_in_zero parameter."""
import numpy as np
import pandas as pd
from microdf import MicroSeries


def test_decile_rank_negatives_in_zero_false():
    """Test default behavior where negative values get assigned to decile 1."""
    values = pd.Series([-100, -50, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    weights = pd.Series(np.ones(len(values)))
    ms = MicroSeries(values, weights=weights)
    
    # Default behavior - negatives get decile 1
    deciles = ms.decile_rank(negatives_in_zero=False)
    
    # Check that negative values get decile 1
    assert deciles[0] == 1  # -100
    assert deciles[1] == 1  # -50
    
    # Check that all values are between 1 and 10
    assert all(1 <= d <= 10 for d in deciles)


def test_decile_rank_negatives_in_zero_true():
    """Test behavior where negative values get assigned to decile 0."""
    values = pd.Series([-100, -50, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    weights = pd.Series(np.ones(len(values)))
    ms = MicroSeries(values, weights=weights)
    
    # With negatives_in_zero=True, negatives get decile 0
    deciles = ms.decile_rank(negatives_in_zero=True)
    
    # Check that negative values get decile 0
    assert deciles[0] == 0  # -100
    assert deciles[1] == 0  # -50
    
    # Check that non-negative values are between 1 and 10
    for i in range(2, len(values)):
        assert 1 <= deciles[i] <= 10


def test_decile_rank_all_negative():
    """Test behavior when all values are negative."""
    values = pd.Series([-100, -90, -80, -70, -60, -50, -40, -30, -20, -10])
    weights = pd.Series(np.ones(len(values)))
    ms = MicroSeries(values, weights=weights)
    
    # Default behavior
    deciles_default = ms.decile_rank(negatives_in_zero=False)
    assert all(1 <= d <= 10 for d in deciles_default)
    
    # With negatives_in_zero=True
    deciles_zero = ms.decile_rank(negatives_in_zero=True)
    assert all(d == 0 for d in deciles_zero)


def test_decile_rank_varied_weights():
    """Test decile rank with varied weights."""
    values = pd.Series([-10, 0, 10, 20, 30, 40, 50, 60, 70, 80])
    weights = pd.Series([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
    ms = MicroSeries(values, weights=weights)
    
    # With negatives_in_zero=True
    deciles = ms.decile_rank(negatives_in_zero=True)
    
    # Negative value should get 0
    assert deciles[0] == 0
    
    # Higher weighted values should tend toward higher deciles
    # The last value (80) with highest weight should be in highest deciles
    assert deciles[9] >= 8


def test_decile_rank_single_negative():
    """Test with a single negative value among many positives."""
    values = pd.Series([-1] + list(range(1, 100)))
    weights = pd.Series(np.ones(len(values)))
    ms = MicroSeries(values, weights=weights)
    
    # With negatives_in_zero=True
    deciles = ms.decile_rank(negatives_in_zero=True)
    
    # Only the negative value should get 0
    assert deciles[0] == 0
    assert all(d >= 1 for d in deciles[1:])


def test_decile_rank_preserves_weights():
    """Test that decile_rank returns a MicroSeries with same weights."""
    values = pd.Series([10, 20, 30, 40, 50])
    weights = pd.Series([1, 2, 3, 4, 5])
    ms = MicroSeries(values, weights=weights)
    
    result = ms.decile_rank()
    
    # Result should be a MicroSeries
    assert isinstance(result, MicroSeries)
    
    # Result should have same weights
    assert result.weights.equals(weights)


if __name__ == "__main__":
    test_decile_rank_negatives_in_zero_false()
    test_decile_rank_negatives_in_zero_true()
    test_decile_rank_all_negative()
    test_decile_rank_varied_weights()
    test_decile_rank_single_negative()
    test_decile_rank_preserves_weights()
    print("All decile_rank tests passed!")