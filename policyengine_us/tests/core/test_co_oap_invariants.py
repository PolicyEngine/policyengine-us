"""Property tests: Colorado Old Age Pension countable income, deeming and floor.

9 CCR 2503-5 3.533(A) counts an OAP client's own income; 3.534(A)-(B) deem
part of a spouse's income to the client, except under 3.534(C) when the
spouse receives Adult Financial grant payments, SSI or Medicaid with income
within the OAP limit; 3.533 and 3.520.781(A) make a client whose total
countable income (SSI included) equals or exceeds the grant standard
ineligible; and 3.530(C), 3.532(B), 3.533(B) raise a grant below the $189
payment floor standard to it.

Each case is a client aged 60-80 in their own household, with pension,
interest, Social Security, earnings, rental income or loss and child support,
optionally receiving outside shelter support, and either single or married to
a spouse who has earnings and a pension and may receive shelter support. Each married case appears four times: (A) the spouse is enrolled in
Medicaid, (B) the spouse is not, (C) as B with extra spousal earnings, and
(D) as B with the tax-unit roles swapped. For 2026:

1. Payment: OAP is the grant standard less total countable income when that
   is positive, raised to the floor if below it, and zero otherwise, with
   cents dropped unless SSI reduces the grant (3.581(E)); so it is zero or
   between the floor and the standard each month.
2. Singles: for a client not on SSI, with no earnings or at least $20 of
   unearned income, 3.533(A) counts the same income as SSI's exclusions
   (20 CFR 416.1112, 416.1124) applied to the same gross income, with
   interest and child support exempt (3.520.786(K), (N)) and a rental loss
   counted as zero (3.520.785(B)(20)). For a client on SSI with none of
   those, 3.533(A) never counts less than SSI does. (PolicyEngine's SSI
   counts interest, which 20 CFR 416.1124(c)(22) excludes on countable
   resources: #10079.)
3. Exemption: a spouse's Medicaid enrollment can only lower the client's
   countable income and raise OAP.
4. Monotonicity: while both spouses' SSI is unchanged, more spousal
   earnings never lower the client's countable income or raise OAP. When
   they change SSI, either can move the other way, as intended: OAP counts
   the client's SSI (an SSI couple aged 65 with no income: $85/month of
   spousal earnings cut each spouse's SSI by $0.02, and OAP rises by as
   much); SSI falling under $20 releases the 3.533(A)(2)(f) spillover; a
   client taken off SSI loses SSA's matching ISM, because Colorado's own ISM
   for clients not on SSI (3.520.79(C)) is not modeled; and a spouse on SSI
   above the OAP limit has SSI deemed (3.534(B)(1)), which their earnings
   below the $65 disregard can lower.
5. Role invariance: the client's countable income and OAP do not depend on
   which spouse is the tax-unit head.

YAML states the worked cases; Python is needed to compare arrangements of
the same household in one simulation and to check against SSI's exclusions.
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.variables.gov.states.co.ssa.oap._precision import ssi_paid
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)

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
                "pension_income": {YEAR: c["client_pension"]},
                "interest_income": {YEAR: c["client_interest"]},
                "social_security_retirement": {YEAR: c["client_social_security"]},
                "employment_income": {YEAR: c["client_earnings"]},
                "rental_income": {YEAR: c["client_rental"]},
                "child_support_received": {YEAR: c["client_child_support"]},
                "ssi_receives_outside_shelter_support": {YEAR: c["shelter_support"]},
                # Set for everyone: an input for some people gives the others
                # its default (false), not its formula.
                "co_oap_medicaid_enrolled": {YEAR: True},
            }
            members = [client]
            if c["married"]:
                extra = c["extra_spouse_earnings"] if arrangement == "C" else 0
                people[spouse] = {
                    "age": {YEAR: c["spouse_age"]},
                    "employment_income": {YEAR: c["spouse_earnings"] + extra},
                    "pension_income": {YEAR: c["spouse_pension"]},
                    "ssi_receives_outside_shelter_support": {
                        YEAR: c["spouse_shelter_support"]
                    },
                    "co_oap_medicaid_enrolled": {YEAR: arrangement == "A"},
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
    """Arrays indexed by person name for every person in every arrangement."""
    simulation = Simulation(situation=build_situation(cases))
    names = list(simulation.populations["person"].ids)
    results = {}
    for variable in (
        "co_oap",
        "co_oap_countable_income",
        "co_oap_own_countable_income",
        "co_oap_eligible",
        "ssi",
        "ssi_countable_income",
        "ssi_earned_income",
        "ssi_unearned_income",
    ):
        values = np.asarray(simulation.calculate(variable, YEAR))
        results[variable] = dict(zip(names, values))
    p = simulation.tax_benefit_system.parameters(f"{YEAR}-01").gov.states.co.ssa.oap
    return results, simulation.tax_benefit_system.parameters, p


def assert_properties(cases, calculated=None):
    results, parameters, p = calculated or calculate(cases)
    standard, floor = p.grant_standard, p.payment_floor
    oap = results["co_oap"]
    countable = results["co_oap_countable_income"]
    eligible = results["co_oap_eligible"]
    ssi = results["ssi"]
    for i, c in enumerate(cases):
        for arrangement in ARRANGEMENTS if c["married"] else "A":
            client = f"client_{arrangement}{i}"
            # Monthly amounts: the inputs and the program are constant
            # within the year.
            # SSI as SSA pays it, as the model counts it.
            total = float(ssi_paid(ssi[client] / 12)) + countable[client] / 12
            paid = oap[client] / 12
            # 1. Payment rule and bounds. Payments not reduced by SSI drop
            # cents (3.581(E)). Within half a cent of the standard, the
            # model's quarter-cent precision decides; YAML pins those.
            grant = standard - total
            if not eligible[client]:
                assert paid == 0, c
            elif grant > 0.005:
                expected = max(grant, floor)
                if ssi[client] > 0:
                    assert paid == pytest.approx(expected, abs=0.05), c
                else:
                    assert abs(paid - round(paid)) < 0.01, c
                    assert expected - 1 < paid <= expected + 0.01, c
                assert floor - TOLERANCE <= paid <= standard + TOLERANCE, c
            elif grant < -0.005:
                assert paid == 0, c
        client = f"client_A{i}"
        if not c["married"]:
            # 2. Singles, against SSI's exclusions on the same gross income:
            # interest and child support exempt (3.520.786(K), (N)), a rental
            # loss counted as zero (3.520.785(B)(20)).
            own = results["co_oap_own_countable_income"][client]
            plain = (
                c["client_interest"] == 0
                and c["client_child_support"] == 0
                and c["client_rental"] >= 0
            )
            # OAP takes each monthly source in cents; SSI does not, so the
            # comparisons allow $0.30/year of rounding.
            if ssi[client] > 0:
                if plain:
                    assert own >= results["ssi_countable_income"][client] - 0.3, c
            elif not c["shelter_support"]:
                unearned = (
                    c["client_pension"]
                    + c["client_social_security"]
                    + max(c["client_rental"], 0)
                )
                if c["client_earnings"] == 0 or unearned >= 20 * 12:
                    expected = _apply_ssi_exclusions(
                        np.array([results["ssi_earned_income"][client]]),
                        np.array([float(unearned)]),
                        parameters,
                        YEAR,
                    )[0]
                    assert own == pytest.approx(expected, abs=0.3), c
            continue
        a, b, c_, d = (f"client_{x}{i}" for x in ARRANGEMENTS)
        # 3. The Medicaid exemption only lowers countable income.
        assert countable[a] <= countable[b] + TOLERANCE, c
        assert oap[a] >= oap[b] - TOLERANCE, c
        # 4. With the client's SSI unchanged, more spousal earnings never
        # lower countable income or raise OAP.
        spouse_b, spouse_c = f"spouse_B{i}", f"spouse_C{i}"
        if ssi[c_] == pytest.approx(ssi[b], abs=TOLERANCE) and ssi[
            spouse_c
        ] == pytest.approx(ssi[spouse_b], abs=TOLERANCE):
            assert countable[c_] >= countable[b] - TOLERANCE, c
            assert oap[c_] <= oap[b] + TOLERANCE, c
        # 5. Roles.
        assert countable[d] == pytest.approx(countable[b], abs=TOLERANCE), c
        assert oap[d] == pytest.approx(oap[b], abs=TOLERANCE), c


def test_worked_example():
    """co_oap YAML Case 22, adding the spouse on Medicaid. The
    client, 62, has no income; the spouse, 50, earns $2,000/month. Without
    Medicaid, 3.534(A) deems (2,000 - 65) / 2 = 967.50 and the grant of
    1,032 - 967.50 = 64.50 is raised to the $189 floor. With the spouse on
    Medicaid, the spouse's own countable income, (2,000 - 65 - 10) / 2 =
    962.50, is within the OAP limit, so nothing is deemed and the client gets
    the full 1,032/month."""
    case = {
        "client_age": 62,
        "client_pension": 0,
        "client_interest": 0,
        "client_social_security": 0,
        "client_earnings": 0,
        "client_rental": 0,
        "client_child_support": 0,
        "shelter_support": False,
        "married": True,
        "spouse_age": 50,
        "spouse_earnings": 24_000,
        "spouse_pension": 0,
        "spouse_shelter_support": False,
        "extra_spouse_earnings": 1_200,
    }
    calculated = calculate([case])
    results = calculated[0]
    oap = results["co_oap"]
    countable = results["co_oap_countable_income"]
    assert oap["client_A0"] == pytest.approx(12_384, abs=TOLERANCE)
    assert countable["client_A0"] == pytest.approx(0, abs=TOLERANCE)
    assert oap["client_B0"] == pytest.approx(2_268, abs=TOLERANCE)
    assert countable["client_B0"] == pytest.approx(11_610, abs=TOLERANCE)
    assert_properties([case], calculated)


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
            "client_age": draw(st.integers(min_value=60, max_value=80)),
            "client_pension": draw(amount(12_000)),
            "client_interest": draw(amount(300)),
            "client_social_security": draw(amount(15_000)),
            "client_earnings": draw(amount(20_000)),
            "client_rental": draw(st.integers(min_value=-6_000, max_value=6_000)),
            "client_child_support": draw(amount(6_000)),
            "shelter_support": draw(st.booleans()),
            "married": draw(st.booleans()),
            "spouse_age": draw(st.integers(min_value=18, max_value=80)),
            "spouse_earnings": draw(amount(30_000)),
            "spouse_pension": draw(amount(24_000)),
            "spouse_shelter_support": draw(st.booleans()),
            "extra_spouse_earnings": draw(st.integers(min_value=1, max_value=12_000)),
        }

    @hypothesis.settings(max_examples=15, deadline=None, suppress_health_check=SLOW)
    @hypothesis.given(st.lists(case(), min_size=1, max_size=8))
    def test_properties(cases):
        assert_properties(cases)
