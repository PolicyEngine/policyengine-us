"""Progressive price indexing reaches reported benefits through the PIA ratio.

Small situations, with no dataset, score a contributed reform that sets
`in_effect`, a 2032 start cohort, a bend-point fraction from the 2035 cohort,
and frozen maximum-career AIME values for the 2035 and 2036 cohorts but a PIA
target for 2035 only. Every value is illustrative and makes no claim about any
percentile. The 2034 cohort therefore has progressive indexing on but no
fraction, and the 2036 cohort has no target: each fails explicitly, so one
reformed system serves all three simulations.

Expected amounts come from an independent rational formula at the model's own
2035 bend points; each AIME sits where the current-law PIA is a whole dime,
so the inverse recovers it exactly. A projection update therefore moves the
inputs and the expectations together.

Python, not YAML: the failure cases assert raised errors, and the expected
values derive from the model's projected bend points.
"""

from fractions import Fraction

import numpy as np
import pytest
from policyengine_core.reforms import Reform

YEAR = 2035
PREFIX = "gov.contrib.ssa.pia."
PROGRESSIVE = PREFIX + "progressive_price_indexing."
FRACTION = Fraction(1, 4)
MAXIMUM_AIME = 17_000
# Born 1973 (FRA 67) and claiming at 62: 1 - 36 * 5/9% - 24 * 5/12% = .70.
CLAIMING_FACTOR = Fraction(7, 10)
# An identified composite ratio of one half: a spousal benefit at the
# spouse's own FRA.
SPOUSE_RATIO = Fraction(1, 2)
GROUPS = ("households", "tax_units", "spm_units", "families", "marital_units")


def _formula(aime, bends):
    first, second = bends
    return (
        Fraction(9, 10) * min(aime, first)
        + Fraction(32, 100) * max(min(aime, second) - first, 0)
        + Fraction(15, 100) * max(aime - second, 0)
    )


def _dime(amount):
    return Fraction(int(amount * 10), 10)


def _exact_dime_aime(near, bends):
    # Between the bends F(A) = .58 * BP1 + .32 * A, a whole dime exactly when
    # A = BP1 (mod 5); the inverse's lower endpoint then recovers A itself.
    aime = bends[0] + 5 * round((near - bends[0]) / 5)
    assert bends[0] < aime < bends[1]
    assert _formula(aime, bends) == _dime(_formula(aime, bends))
    return aime


@pytest.fixture(scope="module")
def system():
    # Share the read-only model; the reform below clones its parameters.
    from policyengine_us.system import system

    return system


@pytest.fixture(scope="module")
def case(system):
    from policyengine_us.tools.social_security.parameters import bend_points_at

    bends = tuple(
        Fraction(str(bend)) for bend in bend_points_at(system.parameters, YEAR)
    )
    threshold = bends[0] + FRACTION * (bends[1] - bends[0])
    protected_pia = _formula(threshold, bends)
    maximum_pia = _formula(MAXIMUM_AIME, bends)
    target = _dime(Fraction(95, 100) * maximum_pia)
    multiplier = (target - protected_pia) / (maximum_pia - protected_pia)
    high = _exact_dime_aime(9_000, bends)
    protected = _exact_dime_aime(3_000, bends)
    assert protected < threshold < high
    assert 0 < multiplier < 1

    def reformed(aime):
        return _dime(
            _formula(min(aime, threshold), bends)
            + multiplier * max(_formula(aime, bends) - protected_pia, 0)
        )

    return dict(
        target=target,
        high=high,
        protected=protected,
        old_high=_formula(high, bends),
        new_high=reformed(high),
        old_protected=_formula(protected, bends),
        new_protected=reformed(protected),
    )


@pytest.fixture(scope="module")
def reformed_system(system, case):
    reform = Reform.from_dict(
        {
            PREFIX + "in_effect": {"2032-01-01": True},
            PROGRESSIVE + "in_effect": {"2032-01-01": True},
            PROGRESSIVE + "start_year": {"2032-01-01": 2032},
            PROGRESSIVE + "bend_point_fraction": {f"{YEAR}-01-01": float(FRACTION)},
            PROGRESSIVE + "maximum_aime": {
                f"{YEAR}-01-01": MAXIMUM_AIME,
                f"{YEAR + 1}-01-01": MAXIMUM_AIME,
            },
            PROGRESSIVE + "maximum_pia_target": {
                f"{YEAR}-01-01": float(case["target"])
            },
        },
        country_id="us",
    )
    result = reform(system)
    result.auto_carry_over_input_variables = system.auto_carry_over_input_variables
    return result


def _simulation(reformed_system, people, units):
    from policyengine_us import Simulation

    situation = {"people": people}
    for plural in GROUPS:
        situation[plural] = {
            name: {"members": members} for name, members in units.items()
        }
    for household in situation["households"].values():
        household["state_code"] = {YEAR: "TX"}
    return Simulation(situation=situation, tax_benefit_system=reformed_system)


def _retiree(eligibility_year, age, annual_benefit, year=YEAR):
    return {
        "age": {year: age},
        "social_security_retirement_worker_eligibility_year": {year: eligibility_year},
        "social_security_retirement_claim_age_months": {year: 744},
        "social_security_retirement_reported": {year: annual_benefit},
    }


def test_progressive_indexing_reaches_worker_and_auxiliary_benefits(
    reformed_system, case
):
    old_high, new_high = case["old_high"], case["new_high"]
    people = {
        "high_earner": _retiree(YEAR, 62, float(12 * CLAIMING_FACTOR * old_high)),
        "spouse": {
            "age": {YEAR: 67},
            "social_security_dependents_worker_id": {YEAR: "high_earner"},
            "social_security_dependents_worker_benefit_ratio": {
                YEAR: float(SPOUSE_RATIO)
            },
            "social_security_dependents_worker_ratio_identified": {YEAR: True},
            "social_security_dependents_reported": {
                YEAR: float(12 * SPOUSE_RATIO * old_high)
            },
        },
        "protected_worker": _retiree(
            YEAR, 62, float(12 * CLAIMING_FACTOR * case["old_protected"])
        ),
        # Eligible in 2031, before the 2032 start cohort.
        "older_cohort": _retiree(2031, 66, 24_000),
    }
    simulation = _simulation(
        reformed_system,
        people,
        {
            "couple": ["high_earner", "spouse"],
            "protected": ["protected_worker"],
            "older": ["older_cohort"],
        },
    )

    def calculate(name):
        return simulation.calculate(name, YEAR)

    assert new_high < old_high
    assert case["new_protected"] == case["old_protected"]
    factor = float(new_high / old_high)
    np.testing.assert_allclose(
        calculate("social_security_retirement_pia_ratio_factor"),
        [factor, 1, 1, 1],
        rtol=1e-6,
    )
    np.testing.assert_allclose(
        calculate("social_security_retirement_inferred_aime")[[0, 2]],
        [float(case["high"]), float(case["protected"])],
    )
    # The spouse's benefit inverts to the worker's AIME and takes the worker's
    # PIA ratio, so the change reaches the auxiliary benefit in proportion.
    np.testing.assert_allclose(
        calculate("social_security_dependents_inferred_aime")[1], float(case["high"])
    )
    np.testing.assert_allclose(
        calculate("social_security_dependents_pia_ratio_factor"),
        [1, factor, 1, 1],
        rtol=1e-6,
    )
    expected_retirement = [
        float(12 * CLAIMING_FACTOR * new_high),
        0,
        float(12 * CLAIMING_FACTOR * case["old_protected"]),
        24_000,
    ]
    expected_dependents = [0, float(12 * SPOUSE_RATIO * new_high), 0, 0]
    np.testing.assert_allclose(
        calculate("social_security_retirement"), expected_retirement, atol=0.01
    )
    np.testing.assert_allclose(
        calculate("social_security_dependents"), expected_dependents, atol=0.01
    )
    np.testing.assert_allclose(
        calculate("social_security"),
        np.add(expected_retirement, expected_dependents),
        atol=0.01,
    )


@pytest.mark.parametrize(
    "eligibility_year,match",
    [
        # Progressive indexing reaches the 2034 cohort, but the fraction
        # starts with the 2035 cohort and no dollar threshold is supplied.
        (
            YEAR - 1,
            "requires a bend-point fraction or a supplied dollar threshold path",
        ),
        # The 2036 cohort has a maximum AIME but no frozen target.
        (
            YEAR + 1,
            f"maximum-career PIA target requires a frozen value for eligibility "
            f"year {YEAR + 1}",
        ),
    ],
)
def test_missing_fraction_or_cohort_value_fails_explicitly(
    reformed_system, case, eligibility_year, match
):
    # Score each worker in their own eligibility year, newly claimed at 62.
    year = max(YEAR, eligibility_year)
    people = {
        "worker": _retiree(
            eligibility_year,
            62 + year - eligibility_year,
            float(12 * CLAIMING_FACTOR * case["old_high"]),
            year,
        )
    }
    simulation = _simulation(reformed_system, people, {"unit": ["worker"]})
    with pytest.raises(ValueError, match=match):
        simulation.calculate("social_security_retirement", year)
