"""Invariants of the monthly SSI in-kind support and maintenance chain.

The ISM chain and SSI countable income are computed per month so that the
food exclusion that took effect September 30, 2024 (89 FR 21199) reaches only
the months it applies to. Everything else is supplied for the whole year, so
nothing else may vary between months. One simulation holds randomized aged
or disabled people in several states with a supplement, with and without
shelter or food support; each check says which months it compares:

1. In 2023 and 2025 every month gives the same countable income, ISM, SSI
   and state supplement, and the annual countable income is twelve times
   one month: annual inputs reach each month as one-twelfth.
2. In 2024 the same holds for everyone without food-only support. With
   food-only support, January to September match one another, October to
   December match one another and count no ISM, and dropping the food ISM
   never lowers SSI.
3. An annual countable income input reaches every month as one-twelfth.

Comparisons against the pre-monthly model on randomized households are
reported on the pull request; they cannot run here, where only one version
of the model exists.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

YEARS = (2023, 2024, 2025)
STATES = ("CA", "CO", "FL", "IN", "KY", "LA", "MO", "MT", "NY", "OK")
SUPPLEMENTS = (
    "co_state_supplement",
    "fl_oss",
    "in_ssp",
    "ky_ssp",
    "la_oss",
    "mo_ssp",
    "mt_ssp",
    "ny_ssp",
    "ok_ssp",
)
N = 60


def _households(seed=2024):
    rng = np.random.default_rng(seed)
    people, households, food_only = {}, {}, []
    for i in range(N):
        food = bool(rng.random() < 0.5)
        shelter = bool(rng.random() < 0.4)
        person = {
            "age": int(rng.choice([40, 66, 75])),
            "is_disabled": bool(rng.random() < 0.6),
            "employment_income": float(rng.choice([0, 0, 2_400, 9_600])),
            "social_security": float(rng.choice([0, 3_600, 7_200])),
            "ssi_receives_food_from_others": food,
            "ssi_receives_outside_shelter_support": shelter,
        }
        if shelter and rng.random() < 0.3:
            person["ssi_shelter_support_value"] = float(rng.choice([1_200, 3_000]))
        people[f"p{i}"] = {
            k: {str(year): v for year in YEARS} for k, v in person.items()
        }
        households[f"h{i}"] = {
            "members": [f"p{i}"],
            "state_code": {str(year): STATES[i % len(STATES)] for year in YEARS},
        }
        food_only.append(food and not shelter)
    # One more person supplies countable income directly, for invariant 3.
    people["direct"] = {"age": {"2025": 70}, "ssi_countable_income": {"2025": 6_000}}
    households["direct"] = {"members": ["direct"], "state_code": {"2025": "FL"}}
    return {"people": people, "households": households}, np.array(food_only)


@pytest.fixture(scope="module")
def results():
    situation, food_only = _households()
    sim = Simulation(situation=situation)
    out = {}
    for year in YEARS:
        for month in range(1, 13):
            period = f"{year}-{month:02d}"
            values = {
                name: sim.calculate(name, period)
                for name in (
                    "ssi_countable_income",
                    "ssi_in_kind_support_and_maintenance",
                    "ssi_pmv_amount",
                    "ssi",
                )
            }
            values["supplement"] = sum(sim.calculate(s, period) for s in SUPPLEMENTS)
            out[period] = values
        out[year] = sim.calculate("ssi_countable_income", year)
    return out, food_only


def _assert_constant(values):
    np.testing.assert_allclose(
        values, np.broadcast_to(values[0], values.shape), atol=1e-6
    )


def _months(out, year, name, months=range(1, 13)):
    return np.stack([out[f"{year}-{m:02d}"][name] for m in months])[:, :N]


@pytest.mark.parametrize("year", [2023, 2025])
def test_months_match_when_nothing_changes_within_the_year(results, year):
    out, _ = results
    for name in ("ssi_countable_income", "ssi_in_kind_support_and_maintenance"):
        values = _months(out, year, name)
        _assert_constant(values)
    for name in ("ssi", "supplement"):
        values = _months(out, year, name)
        _assert_constant(values)
    np.testing.assert_allclose(
        out[year][:N], 12 * _months(out, year, "ssi_countable_income")[0], rtol=1e-6
    )
    # ISM is capped by the PMV, a monthly amount (one-third of the federal
    # benefit rate plus $20, well under $600), not an annual one.
    ism = _months(out, year, "ssi_in_kind_support_and_maintenance")
    pmv = _months(out, year, "ssi_pmv_amount")
    assert np.all(ism <= pmv + 1e-6)
    assert np.all(pmv < 600)


def test_2024_changes_only_food_only_support_from_october(results):
    out, food_only = results
    before = range(1, 10)
    after = range(10, 13)
    for name in ("ssi_countable_income", "ssi", "supplement"):
        values = _months(out, 2024, name)
        others = values[:, ~food_only]
        _assert_constant(others)
        early = _months(out, 2024, name, before)[:, food_only]
        late = _months(out, 2024, name, after)[:, food_only]
        _assert_constant(early)
        _assert_constant(late)
    late_ism = _months(out, 2024, "ssi_in_kind_support_and_maintenance", after)
    assert not late_ism[:, food_only].any()
    ssi_sep = _months(out, 2024, "ssi", [9])[0]
    ssi_oct = _months(out, 2024, "ssi", [10])[0]
    assert np.all(ssi_oct >= ssi_sep - 1e-6)


def test_annual_countable_income_input_reaches_each_month(results):
    out, _ = results
    for month in range(1, 13):
        assert out[f"2025-{month:02d}"]["ssi_countable_income"][-1] == pytest.approx(
            500
        )
