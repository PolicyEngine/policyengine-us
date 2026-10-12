"""Property tests: Colorado AND-CS countable income, deeming and payment floor.

9 CCR 2503-5 3.549(A) counts an AND-CS client's own income; 3.549(C)-(D)
deem part of a spouse's income to the client, except under 3.549(F) when the
spouse receives SSI, Old Age Pension or Medicaid with income within the SSI
limit; 3.520.781(A) makes a client whose total countable income (SSI
included) equals or exceeds the grant standard ineligible; and 3.546(E),
3.549(B) raise a grant below the $13 payment floor standard to it.

Each case is a disabled client aged 18-59 receiving SSI, in their own
household, with pension, interest and earnings, optionally receiving outside
shelter support, and either single or married to a spouse who is not
disabled and has earnings and a pension. Each married case appears four
times: (A) the spouse is enrolled in Medicaid, (B) the spouse is not,
(C) as B with extra spousal earnings, and (D) as B with the tax-unit roles
swapped. For 2026:

1. Payment: the supplement is the grant standard less total countable income
   when that is positive, raised to the floor if below it, and zero otherwise;
   so it is zero or between the floor and the standard.
2. Singles: since 2012 the grant standard has equaled the SSI individual
   benefit rate, and 3.549(A) never counts less than SSI does, so a single
   client in their own household is never paid. Where the client has no
   earnings or at least $20 of unearned income other than SSI, 3.549(A) and
   SSI's exclusions (20 CFR 416.1112, 416.1124) count the same income.
3. Exemption: Medicaid enrollment of a spouse within the SSI limit can only
   lower the client's countable income and raise the supplement.
4. Monotonicity: more earnings for a non-exempt spouse never lower the
   client's countable income or raise the supplement.
5. Role invariance: the client's countable income and supplement do not
   depend on which spouse is the tax-unit head.

YAML states the worked cases; Python is needed to compare arrangements of
the same household in one simulation.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2026
TOLERANCE = 0.01
ARRANGEMENTS = "ABCD"


def build_situation(cases):
    people, groups = (
        {},
        {
            name: {}
            for name in (
                "tax_units",
                "marital_units",
                "spm_units",
                "families",
                "households",
            )
        },
    )
    for i, c in enumerate(cases):
        for arrangement in ARRANGEMENTS if c["married"] else "A":
            key = f"{arrangement}{i}"
            client, spouse = f"client_{key}", f"spouse_{key}"
            people[client] = {
                "age": {YEAR: c["client_age"]},
                "is_disabled": {YEAR: True},
                "meets_ssi_disability_criteria": {YEAR: True},
                "pension_income": {YEAR: c["client_pension"]},
                "interest_income": {YEAR: c["client_interest"]},
                "employment_income": {YEAR: c["client_earnings"]},
                "ssi_receives_outside_shelter_support": {YEAR: c["shelter_support"]},
                # Set for everyone: an input for some people gives the others
                # its default (false), not its formula.
                "medicaid_enrolled_for_ssi_state_supplement": {YEAR: True},
            }
            members = [client]
            if c["married"]:
                extra = c["extra_spouse_earnings"] if arrangement == "C" else 0
                people[spouse] = {
                    "age": {YEAR: c["spouse_age"]},
                    "employment_income": {YEAR: c["spouse_earnings"] + extra},
                    "pension_income": {YEAR: c["spouse_pension"]},
                    "medicaid_enrolled_for_ssi_state_supplement": {
                        YEAR: arrangement == "A"
                    },
                }
                members = [spouse, client] if arrangement == "D" else [client, spouse]
                head, partner = members
                people[head]["is_tax_unit_head"] = {YEAR: True}
                people[head]["is_tax_unit_spouse"] = {YEAR: False}
                people[partner]["is_tax_unit_head"] = {YEAR: False}
                people[partner]["is_tax_unit_spouse"] = {YEAR: True}
            for name, group in groups.items():
                group[f"{name}_{key}"] = {"members": members}
            groups["households"][f"households_{key}"]["state_code"] = {YEAR: "CO"}
    return {"people": people, **groups}


def calculate(cases):
    """Arrays indexed by person name for the client of every arrangement."""
    simulation = Simulation(situation=build_situation(cases))
    names = list(simulation.populations["person"].ids)
    results = {}
    for variable, period in (
        ("co_state_supplement", YEAR),
        ("co_state_supplement_countable_income", YEAR),
        ("co_state_supplement_eligible", f"{YEAR}-01"),
        ("ssi", YEAR),
        ("ssi_countable_income", YEAR),
    ):
        values = np.asarray(simulation.calculate(variable, period))
        results[variable] = dict(zip(names, values))
    parameters = simulation.tax_benefit_system.parameters(f"{YEAR}-01")
    p = parameters.gov.states.co.ssa.state_supplement
    return results, p.grant_standard, p.payment_floor


def assert_properties(cases):
    results, standard, floor = calculate(cases)
    supplement = results["co_state_supplement"]
    countable = results["co_state_supplement_countable_income"]
    eligible = results["co_state_supplement_eligible"]
    ssi = results["ssi"]
    for i, c in enumerate(cases):
        for arrangement in ARRANGEMENTS if c["married"] else "A":
            client = f"client_{arrangement}{i}"
            # Monthly amounts: the inputs and the program are constant
            # within the year.
            total = (ssi[client] + countable[client]) / 12
            paid = supplement[client] / 12
            # 1. Payment rule and bounds.
            if eligible[client] and total < standard - TOLERANCE:
                expected = max(standard - total, floor)
                assert paid == pytest.approx(expected, abs=TOLERANCE), c
                assert floor - TOLERANCE <= paid <= standard + TOLERANCE, c
            elif eligible[client] and total > standard + TOLERANCE:
                assert paid == 0, c
        client = f"client_A{i}"
        if not c["married"]:
            # 2. Singles.
            if ssi[client] > 0:
                assert supplement[client] == 0, c
            assert countable[client] >= results["ssi_countable_income"][client] - (
                TOLERANCE
            ), c
            other_unearned = c["client_pension"] + c["client_interest"]
            if c["client_earnings"] == 0 or other_unearned >= 20 * 12:
                assert countable[client] == pytest.approx(
                    results["ssi_countable_income"][client], abs=TOLERANCE
                ), c
            continue
        a, b, c_, d = (f"client_{x}{i}" for x in ARRANGEMENTS)
        # 3. The Medicaid exemption only lowers countable income.
        assert countable[a] <= countable[b] + TOLERANCE, c
        assert supplement[a] >= supplement[b] - TOLERANCE, c
        # 4. More non-exempt spousal earnings never lower countable income.
        assert countable[c_] >= countable[b] - TOLERANCE, c
        assert supplement[c_] <= supplement[b] + TOLERANCE, c
        # 5. Roles.
        assert countable[d] == pytest.approx(countable[b], abs=TOLERANCE), c
        assert supplement[d] == pytest.approx(supplement[b], abs=TOLERANCE), c


def test_worked_example():
    """co_state_supplement YAML Case 29: the client has no income and the
    spouse earns $1,500/month. With the spouse on Medicaid, SSI pays 783.50
    and 3.549(F) deems nothing: 994 - 783.50 = 210.50/month. Without
    Medicaid, 3.549(C) deems (1,500 - 65) / 2 = 717.50 and the client is not
    eligible."""
    case = {
        "client_age": 40,
        "client_pension": 0,
        "client_interest": 0,
        "client_earnings": 0,
        "shelter_support": False,
        "married": True,
        "spouse_age": 42,
        "spouse_earnings": 18_000,
        "spouse_pension": 0,
        "extra_spouse_earnings": 1_200,
    }
    results, _, _ = calculate([case])
    supplement = results["co_state_supplement"]
    countable = results["co_state_supplement_countable_income"]
    assert supplement["client_A0"] == pytest.approx(2_526, abs=TOLERANCE)
    assert countable["client_A0"] == pytest.approx(0, abs=TOLERANCE)
    assert supplement["client_B0"] == 0
    assert countable["client_B0"] == pytest.approx(8_610, abs=TOLERANCE)
    assert_properties([case])


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
            "client_age": draw(st.integers(min_value=18, max_value=59)),
            "client_pension": draw(amount(12_000)),
            "client_interest": draw(amount(300)),
            "client_earnings": draw(amount(20_000)),
            "shelter_support": draw(st.booleans()),
            "married": draw(st.booleans()),
            "spouse_age": draw(st.integers(min_value=18, max_value=59)),
            "spouse_earnings": draw(amount(30_000)),
            "spouse_pension": draw(amount(12_000)),
            "extra_spouse_earnings": draw(st.integers(min_value=1, max_value=12_000)),
        }

    @hypothesis.settings(max_examples=15, deadline=None, suppress_health_check=SLOW)
    @hypothesis.given(st.lists(case(), min_size=1, max_size=8))
    def test_properties(cases):
        assert_properties(cases)
