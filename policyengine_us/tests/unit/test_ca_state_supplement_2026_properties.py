"""Properties of California's 2026 SSI state supplement.

Each test evaluates every point of a Social Security income grid in one
vectorized simulation, for an aged individual or an aged couple living
independently, with and without cooking facilities. The expected payment
levels are the published January 2026 figures, not PolicyEngine parameters:
CDSS, "SSI Total Monthly Payment Amounts 2026", and SSA POMS SI 01415.058
(California recipient and couple payment levels).

For every grid point:

- the supplement matches the reference max(0, standard - max(FBR, countable));
- SSI, the supplement and countable income sum to max(standard, countable);
- while countable income is at most the federal benefit rate, the supplement
  is the state supplement level POMS lists (standard - FBR);
- the supplement is non-negative, at most standard - FBR, and does not rise
  with income.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

PERIOD = "2026-01"
YEAR = 2026

# SSI's $20 general income exclusion, 20 CFR 416.1124(c)(12).
GENERAL_EXCLUSION = 20

# Monthly Social Security amounts around the federal benefit rate and the
# California payment standards.
MONTHLY_SOCIAL_SECURITY = np.array(
    [
        0,
        1,
        20,
        21,
        500,
        1_013,
        1_014,
        1_015,
        1_100,
        1_253.94,
        1_382.81,
        1_511,
        2_118.83,
        2_376.57,
        2_500,
        5_000,
    ]
)

# (federal benefit rate, payment standard with cooking facilities, payment
# standard without cooking facilities), monthly, January 2026.
LEVELS = {
    "individual": (994, 1_233.94, 1_362.81),
    "couple": (1_491, 2_098.83, 2_356.57),
}


def grid_simulation(unit, cooking):
    """One aged household per grid point; the head receives the income."""
    situation = {
        "people": {},
        "tax_units": {},
        "marital_units": {},
        "spm_units": {},
        "households": {},
    }
    for i, monthly in enumerate(MONTHLY_SOCIAL_SECURITY):
        head = f"head{i}"
        members = [head]
        situation["people"][head] = {
            "age": {YEAR: 70},
            "social_security_retirement": {YEAR: float(monthly) * 12},
        }
        if unit == "couple":
            spouse = f"spouse{i}"
            members.append(spouse)
            situation["people"][spouse] = {"age": {YEAR: 68}}
        situation["tax_units"][f"t{i}"] = {"members": members}
        situation["marital_units"][f"m{i}"] = {"members": members}
        situation["spm_units"][f"s{i}"] = {"members": members}
        situation["households"][f"h{i}"] = {
            "members": members,
            "state_code": {YEAR: "CA"},
            "living_arrangements_allow_for_food_preparation": {YEAR: cooking},
        }
    return Simulation(situation=situation)


@pytest.mark.parametrize("unit", ["individual", "couple"])
@pytest.mark.parametrize("cooking", [True, False])
def test_ca_state_supplement_2026_properties(unit, cooking):
    fbr, with_cooking, without_cooking = LEVELS[unit]
    standard = with_cooking if cooking else without_cooking
    sim = grid_simulation(unit, cooking)

    countable = np.maximum(MONTHLY_SOCIAL_SECURITY - GENERAL_EXCLUSION, 0)
    ssi = sim.calculate("ssi", PERIOD)
    ssi = ssi.reshape(len(MONTHLY_SOCIAL_SECURITY), -1).sum(axis=1)
    supplement = sim.calculate("ca_state_supplement", PERIOD)
    payment_standard = sim.calculate("ca_state_supplement_payment_standard", PERIOD)

    np.testing.assert_allclose(payment_standard, standard, atol=0.01)
    np.testing.assert_allclose(ssi, np.maximum(fbr - countable, 0), atol=0.01)
    reference = np.maximum(0, standard - np.maximum(fbr, countable))
    np.testing.assert_allclose(supplement, reference, atol=0.01)
    np.testing.assert_allclose(
        ssi + supplement + countable,
        np.maximum(standard, countable),
        atol=0.01,
    )

    below_fbr = countable <= fbr
    np.testing.assert_allclose(supplement[below_fbr], standard - fbr, atol=0.01)
    assert np.all(supplement >= 0)
    assert np.all(supplement <= standard - fbr + 0.01)
    assert np.all(np.diff(supplement) <= 0.01), "rises with income"
    # Guard against a vacuous pass: the grid reaches both sides of the
    # federal benefit rate and income above the payment standard.
    assert below_fbr.any() and (~below_fbr).any()
    assert (supplement == 0).any() and (supplement > 0).any()
