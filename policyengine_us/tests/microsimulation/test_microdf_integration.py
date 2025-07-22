"""Integration tests for microdf functionality in policyengine-us."""
import pytest
import numpy as np
from policyengine_us import Microsimulation


def test_spm_unit_income_decile_microsimulation():
    """Test that spm_unit_income_decile works correctly in microsimulation."""
    sim = Microsimulation()
    
    # Get the deciles
    deciles = sim.calculate("spm_unit_income_decile", 2024)
    
    # Check that all values are between 1 and 10
    assert np.all((deciles >= 1) & (deciles <= 10)), "All deciles should be between 1 and 10"
    
    # Check that we have all deciles represented (with enough data)
    unique_deciles = np.unique(deciles)
    assert len(unique_deciles) == 10, "Should have all 10 deciles represented"
    
    # Check that deciles are properly distributed (roughly 10% in each)
    weights = sim.calculate("spm_unit_weight", 2024) * sim.calculate("spm_unit_nb_members", 2024)
    total_weight = weights.sum()
    
    for decile in range(1, 11):
        decile_weight = weights[deciles == decile].sum()
        decile_percentage = decile_weight / total_weight
        # Allow for some variation due to discrete assignment
        assert 0.05 < decile_percentage < 0.15, f"Decile {decile} has {decile_percentage:.1%} of weight"


def test_household_income_decile_microsimulation():
    """Test that household_income_decile works correctly in microsimulation."""
    sim = Microsimulation()
    
    # Get the deciles
    deciles = sim.calculate("household_income_decile", 2024)
    
    # Check that values are either -1 or between 1 and 10
    assert np.all((deciles == -1) | ((deciles >= 1) & (deciles <= 10))), \
        "All deciles should be -1 or between 1 and 10"
    
    # Check that negative income households get -1
    income = sim.calculate("household_net_income", 2024)
    negative_income_mask = income < 0
    if negative_income_mask.any():
        assert np.all(deciles[negative_income_mask] == -1), \
            "Households with negative income should have decile -1"
    
    # Check positive income households
    positive_income_mask = income >= 0
    positive_deciles = deciles[positive_income_mask]
    assert np.all((positive_deciles >= 1) & (positive_deciles <= 10)), \
        "Positive income households should have deciles 1-10"
    
    # Check distribution of positive deciles
    weights = sim.calculate("household_weight", 2024) * sim.calculate("household_count_people", 2024)
    positive_weights = weights[positive_income_mask]
    total_positive_weight = positive_weights.sum()
    
    # Check roughly equal distribution (allowing for variation)
    for decile in range(1, 11):
        decile_mask = positive_deciles == decile
        if decile_mask.any():
            decile_weight = positive_weights[decile_mask].sum()
            decile_percentage = decile_weight / total_positive_weight
            # Allow for more variation as distribution may not be perfectly uniform
            assert 0.02 < decile_percentage < 0.20, \
                f"Decile {decile} has {decile_percentage:.1%} of positive income weight"


def test_decile_rank_consistency():
    """Test that decile ranks are consistent with income ordering."""
    sim = Microsimulation()
    
    # Test SPM unit deciles
    spm_income = sim.calculate("spm_unit_oecd_equiv_net_income", 2024)
    spm_deciles = sim.calculate("spm_unit_income_decile", 2024)
    
    # For each decile, check that higher deciles have higher average income
    for d1 in range(1, 10):
        for d2 in range(d1 + 1, 11):
            income_d1 = spm_income[spm_deciles == d1].mean()
            income_d2 = spm_income[spm_deciles == d2].mean()
            assert income_d1 <= income_d2, \
                f"SPM decile {d1} (avg income {income_d1:.0f}) should have lower income than decile {d2} (avg income {income_d2:.0f})"
    
    # Test household deciles (excluding negative income households)
    hh_income = sim.calculate("household_net_income", 2024)
    hh_deciles = sim.calculate("household_income_decile", 2024)
    
    # Only check positive income households
    positive_mask = hh_income >= 0
    positive_income = hh_income[positive_mask]
    positive_deciles = hh_deciles[positive_mask]
    
    for d1 in range(1, 10):
        for d2 in range(d1 + 1, 11):
            mask_d1 = positive_deciles == d1
            mask_d2 = positive_deciles == d2
            if mask_d1.any() and mask_d2.any():
                income_d1 = positive_income[mask_d1].mean()
                income_d2 = positive_income[mask_d2].mean()
                assert income_d1 <= income_d2, \
                    f"Household decile {d1} (avg income {income_d1:.0f}) should have lower income than decile {d2} (avg income {income_d2:.0f})"


def test_microdf_weighted_calculations():
    """Test that microdf properly handles weighted calculations."""
    sim = Microsimulation()
    
    # Get weights and counts for SPM units
    spm_weights = sim.calculate("spm_unit_weight", 2024)
    spm_members = sim.calculate("spm_unit_nb_members", 2024)
    
    # The weighted calculation should use weights * nb_persons
    total_weighted_persons = (spm_weights * spm_members).sum()
    
    # This should represent roughly the US population
    # Allow for some variation but should be in the hundreds of millions
    assert 100_000_000 < total_weighted_persons < 500_000_000, \
        f"Total weighted persons ({total_weighted_persons:,.0f}) seems unrealistic"
    
    # Similar check for households
    hh_weights = sim.calculate("household_weight", 2024)
    hh_count = sim.calculate("household_count_people", 2024)
    
    total_hh_weighted_persons = (hh_weights * hh_count).sum()
    assert 100_000_000 < total_hh_weighted_persons < 500_000_000, \
        f"Total household weighted persons ({total_hh_weighted_persons:,.0f}) seems unrealistic"


if __name__ == "__main__":
    # Run the tests
    test_spm_unit_income_decile_microsimulation()
    test_household_income_decile_microsimulation()
    test_decile_rank_consistency()
    test_microdf_weighted_calculations()
    print("All microdf integration tests passed!")