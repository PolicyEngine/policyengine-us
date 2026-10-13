"""Property tests: Colorado Adult Financial in-kind support and maintenance.

9 CCR 2503-5 3.520.79 counts in-kind support and maintenance (ISM) as
unearned income of an Old Age Pension or AND-CS client. Under 3.520.79(B)(6)
and 3.520.71(E), an SSI recipient whom SSA charges ISM is charged "a matching
ISM" ("an identical ISM amount"); other clients are counted up to the maximum
ISM (3.520.79(C), $351 in 2026).

Each case is a disabled SSI client aged 18-59 with a disability benefit and
earnings, single or married to a disabled spouse with the same arrangement,
in 2026. Each case appears twice, as a twin with no in-kind support (N) and
as one receiving it (S): in another person's household under SSI's
one-third reduction, or in their own household with outside shelter support,
optionally of a given value. A third set of people are clients aged 62
without SSI, receiving shelter support of a drawn value.

1. Matching (differential): an SSI recipient's ISM equals SSA's. Under the
   one-third reduction this is the cut SSA made to the benefit rate, the
   twins' ssi_amount_if_eligible difference; otherwise it is SSI's presumed
   maximum value ISM, halved for a couple.
2. Bounds: ISM is non-negative, and an SSI recipient's is no more than the
   presumed maximum value, one-third of the benefit rate plus $20.
3. No backfill: receiving in-kind support lowers SSI plus AND-CS by at least
   SSA's ISM less the client's share of the $20 disregard (3.549(A)(2)) and
   less any state supplementary payment that raises a grant to the $13
   floor (3.549(B)), so AND-CS restores no more of SSA's reduction than
   those.
4. Payment, not value: a client without SSI who receives shelter from
   others, and so pays none (3.520.79(C)(3)), is counted the $351 maximum
   whatever the shelter is worth.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2026
PERIOD = f"{YEAR}-01"
TOLERANCE = 0.01
GROUPS = ("tax_units", "marital_units", "spm_units", "families", "households")


def _add_unit(groups, key, members):
    for name in GROUPS:
        groups[name][f"{name}_{key}"] = {"members": members}
    groups["households"][f"households_{key}"]["state_code"] = {YEAR: "CO"}


def _arrangement_inputs(arrangement, value):
    if arrangement == "another_household":
        return {
            "ssi_lives_in_another_persons_household": {PERIOD: True},
            "ssi_receives_shelter_from_others_in_household": {PERIOD: True},
            "ssi_others_pay_all_meals": {PERIOD: True},
        }
    inputs = {"ssi_receives_outside_shelter_support": {PERIOD: True}}
    if value:
        inputs["ssi_shelter_support_value"] = {YEAR: value * 12}
    return inputs


def build_situation(cases, values):
    people = {}
    groups = {name: {} for name in GROUPS}
    for i, c in enumerate(cases):
        for twin in "NS":
            key = f"{twin}{i}"
            members = []
            for role in ("client", "spouse") if c["married"] else ("client",):
                name = f"{role}_{key}"
                people[name] = {
                    "age": {YEAR: c[f"{role}_age"]},
                    "is_disabled": {YEAR: True},
                    "meets_ssi_disability_criteria": {YEAR: True},
                    "social_security_disability": {YEAR: c[f"{role}_ssdi"] * 12},
                    "employment_income": {YEAR: c[f"{role}_earnings"] * 12},
                }
                if twin == "S":
                    people[name].update(
                        _arrangement_inputs(c["arrangement"], c["support_value"])
                    )
                members.append(name)
            if c["married"]:
                people[members[0]]["is_tax_unit_head"] = {YEAR: True}
                people[members[1]]["is_tax_unit_spouse"] = {YEAR: True}
            _add_unit(groups, key, members)
    for j, value in enumerate(values):
        name = f"older_{j}"
        people[name] = {
            "age": {YEAR: 62},
            "pension_income": {YEAR: 12_000},
            "ssi_receives_outside_shelter_support": {PERIOD: True},
            "ssi_shelter_support_value": {YEAR: value * 12},
        }
        _add_unit(groups, f"older_{j}", [name])
    return {"people": people, **groups}


def calculate(cases, values):
    simulation = Simulation(situation=build_situation(cases, values))
    names = list(simulation.populations["person"].ids)
    results = {}
    for variable in (
        "co_ssa_in_kind_support_and_maintenance",
        "co_state_supplement",
        "co_state_supplement_countable_income",
        "ssi",
        "ssi_amount_if_eligible",
        "ssi_in_kind_support_and_maintenance",
        "ssi_couple_computation_applies",
    ):
        period = YEAR if variable == "ssi_in_kind_support_and_maintenance" else PERIOD
        values_ = np.asarray(simulation.calculate(variable, period))
        if variable == "ssi_in_kind_support_and_maintenance":
            values_ = values_ / 12
        results[variable] = dict(zip(names, values_))
    p = simulation.tax_benefit_system.parameters(PERIOD)
    return results, p


def assert_properties(cases, values):
    results, p = calculate(cases, values)
    ism = results["co_ssa_in_kind_support_and_maintenance"]
    supplement = results["co_state_supplement"]
    ssi = results["ssi"]
    rate = results["ssi_amount_if_eligible"]
    maximum = p.gov.states.co.ssa.ism.maximum
    individual_pmv = p.gov.ssa.ssi.amount.individual / 3 + 20
    and_cs = p.gov.states.co.ssa.state_supplement
    disregard = and_cs.income.disregards.unearned
    countable = results["co_state_supplement_countable_income"]
    for i, c in enumerate(cases):
        roles = ("client", "spouse") if c["married"] else ("client",)
        for role in roles:
            n, s = f"{role}_N{i}", f"{role}_S{i}"
            # 2. Bounds.
            assert ism[n] == 0, c
            assert -TOLERANCE <= ism[s] <= individual_pmv + TOLERANCE, c
            if ssi[s] <= 0:
                continue
            # 1. Matching.
            if c["arrangement"] == "another_household":
                expected = rate[n] - rate[s]
            else:
                expected = results["ssi_in_kind_support_and_maintenance"][s]
                if results["ssi_couple_computation_applies"][s]:
                    expected /= 2
            assert ism[s] == pytest.approx(expected, abs=TOLERANCE), c
            # 3. No backfill.
            share = disregard / 2 if c["married"] else disregard
            grant = max(0, and_cs.grant_standard - ssi[s] - countable[s])
            floor_top_up = supplement[s] - grant if supplement[s] > 0 else 0
            drop = ssi[n] + supplement[n] - ssi[s] - supplement[s]
            assert drop >= ism[s] - share - floor_top_up - TOLERANCE, c
    for j, value in enumerate(values):
        # 4. Payment, not value.
        assert ism[f"older_{j}"] == pytest.approx(maximum, abs=TOLERANCE), value


def test_worked_examples():
    """co_state_supplement YAML Cases 28 and 32, monthly: a single client in
    another person's household is charged 331.33 and paid $20; each member of
    a couple is charged 248.50 and paid 258.50. A client without SSI who
    pays nothing is counted the $351 maximum, whatever the support is
    worth."""
    single = {
        "married": False,
        "client_age": 40,
        "client_ssdi": 0,
        "client_earnings": 0,
        "spouse_age": 40,
        "spouse_ssdi": 0,
        "spouse_earnings": 0,
        "arrangement": "another_household",
        "support_value": 0,
    }
    couple = {**single, "married": True, "client_age": 50, "spouse_age": 52}
    results, _ = calculate([single, couple], [0, 200, 400])
    ism = results["co_ssa_in_kind_support_and_maintenance"]
    supplement = results["co_state_supplement"]
    assert ism["client_S0"] == pytest.approx(331.33, abs=TOLERANCE)
    assert supplement["client_S0"] == pytest.approx(20, abs=TOLERANCE)
    assert ism["client_S1"] == pytest.approx(248.50, abs=TOLERANCE)
    assert supplement["spouse_S1"] == pytest.approx(258.50, abs=TOLERANCE)
    assert ism["older_0"] == pytest.approx(351, abs=TOLERANCE)
    assert ism["older_1"] == pytest.approx(351, abs=TOLERANCE)
    assert ism["older_2"] == pytest.approx(351, abs=TOLERANCE)
    assert_properties([single, couple], [0, 200, 400])


try:
    import hypothesis
    import hypothesis.strategies as st
except ImportError:  # pragma: no cover
    hypothesis = None

if hypothesis is not None:
    # Each example builds a Simulation; on a loaded runner input generation
    # can trip the too_slow health check, which says nothing about the model.
    SLOW = [hypothesis.HealthCheck.too_slow]

    def amount(high):
        return st.one_of(st.just(0), st.integers(min_value=1, max_value=high))

    @st.composite
    def case(draw):
        return {
            "married": draw(st.booleans()),
            "client_age": draw(st.integers(min_value=18, max_value=59)),
            "client_ssdi": draw(amount(1_200)),
            "client_earnings": draw(amount(1_500)),
            "spouse_age": draw(st.integers(min_value=18, max_value=59)),
            "spouse_ssdi": draw(amount(1_200)),
            "spouse_earnings": draw(amount(1_500)),
            "arrangement": draw(st.sampled_from(["another_household", "outside"])),
            "support_value": draw(amount(500)),
        }

    # Review counterexample: the supported spouse's $10 grant is raised to
    # the $13 floor.
    FLOOR_CASE = {
        "married": True,
        "client_age": 18,
        "client_ssdi": 0,
        "client_earnings": 1_145,
        "spouse_age": 18,
        "spouse_ssdi": 0,
        "spouse_earnings": 106,
        "arrangement": "another_household",
        "support_value": 0,
    }

    @hypothesis.settings(max_examples=15, deadline=None, suppress_health_check=SLOW)
    @hypothesis.example(cases=[FLOOR_CASE], values=[0])
    @hypothesis.given(
        st.lists(case(), min_size=1, max_size=8),
        st.lists(amount(500), min_size=1, max_size=6),
    )
    def test_properties(cases, values):
        assert_properties(cases, values)
