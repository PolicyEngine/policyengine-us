"""Property tests: premiums and the $300 exclusions in Michigan household resources.

MI-1040CR line 30 subtracts "total adjustments from your U.S. Form 1040,
Schedule 1", which include the self-employed health insurance deduction
(Schedule 1 line 17). Line 31 subtracts "insurance premiums you paid for
yourself and your family", but "Do not include any insurance premiums deducted
on lines 21 or 30" (2025 MI-1040 book, page 33).

MCL 206.510(1) excludes from income "(a) The first $300.00 of gifts in cash or
kind from nongovernmental sources" and "(b) The first $300.00 received from
awards, prizes, lottery, bingo, or other gambling winnings". The MI-1040CR
enters gambling winnings "over $300" on line 20 and "the value over $300 in
gifts" on line 24 (page 32), each one amount for the claimant and spouse.
Gifts are financial_assistance, cash from friends or relatives outside the
household.

So for every household:

1. Each premium dollar is subtracted once. Zeroing every member's premiums
   raises household resources by between 0 and the household's total
   premiums, and by exactly that total when household resources were
   positive.
2. Household resources are non-decreasing in the head's gambling winnings.
   They do not change while the claimant's and spouse's winnings total at
   most $300, and when they were positive they rise by the change in
   winnings over $300.
3. The same holds for gifts.
4. A reform that drops the self-employed health insurance deduction from the
   federal list moves those premiums from line 30 to line 31 and leaves
   household resources unchanged.

The households have a head, an optional spouse and an optional dependent, who
may be self-employed and pay premiums. SSI and the Family Independence
Program grant are inputs set to zero, so more gifts cannot lower a computed
benefit. Comparisons allow one cent or eight float32 spacings at the sum of
the household's absolute amounts, as in test_mi_household_resources_losses.py.
"""

import numpy as np
import pytest

from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation

YEAR = 2025
TOLERANCE = 0.01
# MCL 206.510(1)(a) and (b): a fixed amount in the statute, not indexed.
EXCLUSION = 300

AMOUNTS = [
    "employment_income_before_lsr",
    "self_employment_income",
    "health_insurance_premiums",
    "gambling_winnings",
    "financial_assistance",
]
PREMIUMS = "health_insurance_premiums"


def person(**amounts):
    p = {name: 0 for name in AMOUNTS}
    p["is_self_employed"] = False
    p.update(amounts)
    return p


def build_situation(households):
    """One Michigan tax unit per household: a head aged 45, an optional
    spouse aged 44 and an optional dependent aged 16."""
    people, tax_units, marital_units, spm_units, households_out = {}, {}, {}, {}, {}
    for i, h in enumerate(households):
        members, couple = [], []
        roles = [("head", h["head"])]
        if h.get("spouse") is not None:
            roles.append(("spouse", h["spouse"]))
        if h.get("dependent") is not None:
            roles.append(("dependent", h["dependent"]))
        for j, (role, p) in enumerate(roles):
            name = f"person_{i}_{j}"
            people[name] = {
                "age": {YEAR: {"head": 45, "spouse": 44}.get(role, 16)},
                "is_tax_unit_head": {YEAR: role == "head"},
                "is_tax_unit_spouse": {YEAR: role == "spouse"},
                "is_tax_unit_dependent": {YEAR: role == "dependent"},
                "ssi": {YEAR: 0},
                **{name_: {YEAR: p[name_]} for name_ in [*AMOUNTS, "is_self_employed"]},
            }
            members.append(name)
            if role == "dependent":
                marital_units[f"marital_unit_{i}_{j}"] = {"members": [name]}
            else:
                couple.append(name)
        tax_units[f"tax_unit_{i}"] = {"members": members}
        marital_units[f"marital_unit_{i}"] = {"members": couple}
        spm_units[f"spm_unit_{i}"] = {"members": members, "tanf": {YEAR: 0}}
        households_out[f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "MI"},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "spm_units": spm_units,
        "households": households_out,
    }


def calculate(households):
    simulation = Simulation(situation=build_situation(households))
    return np.asarray(simulation.calculate("mi_household_resources", YEAR))


def members(h):
    return [p for p in (h["head"], h.get("spouse"), h.get("dependent")) if p]


def filers(h):
    return [p for p in (h["head"], h.get("spouse")) if p]


def total(people, name):
    return sum(p[name] for p in people)


def copy(h):
    return {
        role: (dict(h[role]) if h.get(role) is not None else None)
        for role in ("head", "spouse", "dependent")
    }


def tolerance(h):
    """One cent, or eight float32 spacings at the sum of the household's
    absolute amounts."""
    scale = sum(abs(p[name]) for p in members(h) for name in AMOUNTS)
    return max(TOLERANCE, 8 * float(np.spacing(np.float32(scale))))


def over_exclusion(amount):
    return max(0, amount - EXCLUSION)


def assert_premiums_subtracted_once(households):
    """Property 1."""
    zeroed = []
    for h in households:
        z = copy(h)
        for p in members(z):
            p[PREMIUMS] = 0
        zeroed.append(z)
    result = calculate(households + zeroed)
    n = len(households)
    for i, h in enumerate(households):
        tol = tolerance(h)
        premiums = total(members(h), PREMIUMS)
        subtracted = float(result[n + i]) - float(result[i])
        assert -tol <= subtracted <= premiums + tol, h
        if result[i] > tol:
            assert subtracted == pytest.approx(premiums, abs=tol), h


def assert_exclusion(households, name, extra):
    """Properties 2 and 3: raise the head's amount of name by extra."""
    raised = []
    for h in households:
        r = copy(h)
        r["head"][name] += extra
        raised.append(r)
    result = calculate(households + raised)
    n = len(households)
    for i, h in enumerate(households):
        tol = tolerance(raised[i])
        before = total(filers(h), name)
        after = before + extra
        change = float(result[n + i]) - float(result[i])
        assert change >= -tol, (h, name, extra)
        if after <= EXCLUSION:
            assert change == pytest.approx(0, abs=tol), (h, name, extra)
        if result[i] > tol:
            expected = over_exclusion(after) - over_exclusion(before)
            assert change == pytest.approx(expected, abs=tol), (h, name, extra)


# ---------------------------------------------------------------------------
# Deterministic tests (no Hypothesis needed).
# ---------------------------------------------------------------------------


def test_self_employed_premiums_subtracted_once():
    """The self-employed health insurance deduction (line 30) and line 31
    together subtract each premium once: for a self-employed claimant, a
    self-employed couple, premiums above the deduction's earnings limit, and
    a self-employed dependent whose premium the claimant is read to pay."""
    households = [
        {"head": person(self_employment_income=50_000, **{PREMIUMS: 5_000})},
        {
            "head": person(
                employment_income_before_lsr=40_000,
                self_employment_income=3_000,
                **{PREMIUMS: 5_000},
            )
        },
        {
            "head": person(self_employment_income=60_000, **{PREMIUMS: 4_000}),
            "spouse": person(self_employment_income=20_000, **{PREMIUMS: 3_000}),
        },
        {
            "head": person(employment_income_before_lsr=40_000, **{PREMIUMS: 2_000}),
            "dependent": person(self_employment_income=8_000, **{PREMIUMS: 1_000}),
        },
    ]
    for h in households:
        for p in members(h):
            p["is_self_employed"] = p["self_employment_income"] > 0
    assert_premiums_subtracted_once(households)


def without_self_employed_health_insurance_ald():
    """A reform that removes the self-employed health insurance deduction
    from gov.irs.ald.deductions."""

    class reform(Reform):
        def apply(self):
            def modify(parameters):
                deductions = parameters.gov.irs.ald.deductions
                values = [
                    d
                    for d in deductions(f"{YEAR}-01-01")
                    if d != "self_employed_health_insurance_ald"
                ]
                deductions.update(
                    start=instant(f"{YEAR}-01-01"),
                    stop=instant(f"{YEAR}-12-31"),
                    value=values,
                )
                return parameters

            self.modify_parameters(modify)

    return reform


def test_premiums_move_to_line_31_without_the_federal_deduction():
    """Without the federal deduction, line 30 no longer subtracts the
    premiums, so line 31 does: household resources are unchanged, and the
    premiums still come off once."""
    households = [
        {"head": person(self_employment_income=50_000, **{PREMIUMS: 5_000})},
        {
            "head": person(
                employment_income_before_lsr=40_000,
                self_employment_income=3_000,
                **{PREMIUMS: 5_000},
            )
        },
    ]
    for h in households:
        h["head"]["is_self_employed"] = True
    situation = build_situation(households)
    baseline = Simulation(situation=situation)
    reformed = Simulation(
        situation=situation, reform=without_self_employed_health_insurance_ald()
    )
    # The reform takes the deduction (5,000 and 3,000) out of federal AGI.
    deduction = baseline.calculate("self_employed_health_insurance_ald", YEAR)
    assert deduction == pytest.approx([5_000, 3_000], abs=TOLERANCE)
    agi_change = reformed.calculate("adjusted_gross_income", YEAR) - baseline.calculate(
        "adjusted_gross_income", YEAR
    )
    assert agi_change == pytest.approx(deduction, abs=TOLERANCE)
    expected = baseline.calculate("mi_household_resources", YEAR)
    result = reformed.calculate("mi_household_resources", YEAR)
    assert result == pytest.approx(expected, abs=TOLERANCE)
    # Line 33 from the form: 50,000 - 3,532.39 - 5,000 and
    # 43,000 - 211.94 - 5,000.
    assert result == pytest.approx([41_467.61, 37_788.06], abs=TOLERANCE)


@pytest.mark.parametrize("name", ["gambling_winnings", "financial_assistance"])
def test_exclusion_grid(name):
    """For single and joint claimants, every step from 0 to $1,000 in $100s:
    nothing counts until the claimant's and spouse's total passes $300."""
    households = []
    for spouse_amount in [None, 0, 200]:
        for start in range(0, 1_000, 100):
            h = {"head": person(employment_income_before_lsr=20_000, **{name: start})}
            if spouse_amount is not None:
                h["spouse"] = person(**{name: spouse_amount})
            households.append(h)
    assert_exclusion(households, name, 100)


def test_dependent_amounts_do_not_use_the_exclusion():
    """A dependent's own winnings and gifts are on the dependent's return:
    they neither count nor use up the claimant's $300."""
    base = {
        "head": person(employment_income_before_lsr=20_000),
        "dependent": person(gambling_winnings=5_000, financial_assistance=5_000),
    }
    with_head = copy(base)
    with_head["head"]["gambling_winnings"] = 500
    with_head["head"]["financial_assistance"] = 500
    result = calculate([base, with_head])
    assert result[0] == pytest.approx(20_000, abs=TOLERANCE)
    assert result[1] == pytest.approx(20_000 + 200 + 200, abs=TOLERANCE)


# ---------------------------------------------------------------------------
# Hypothesis properties. Hypothesis is a dev extra: without it these tests
# are not collected and the deterministic tests above still run.
# ---------------------------------------------------------------------------

try:
    import hypothesis
    import hypothesis.strategies as st
except ImportError:  # pragma: no cover
    hypothesis = None

if hypothesis is not None:
    # Each example builds a Simulation; on a loaded runner input generation
    # can trip the too_slow health check, which says nothing about the model.
    SLOW = [hypothesis.HealthCheck.too_slow]
    INCOME = st.one_of(st.just(0), st.integers(min_value=100, max_value=150_000))
    SELF_EMPLOYMENT = st.one_of(
        st.just(0), st.integers(min_value=-30_000, max_value=150_000)
    )
    PREMIUM = st.one_of(st.just(0), st.integers(min_value=100, max_value=20_000))
    # Small amounts, so that many households stay within the $300.
    SMALL = st.one_of(st.just(0), st.integers(min_value=1, max_value=1_000))

    @st.composite
    def a_person(draw):
        return person(
            employment_income_before_lsr=draw(INCOME),
            self_employment_income=draw(SELF_EMPLOYMENT),
            is_self_employed=draw(st.booleans()),
            gambling_winnings=draw(SMALL),
            financial_assistance=draw(SMALL),
            **{PREMIUMS: draw(PREMIUM)},
        )

    @st.composite
    def household(draw):
        return {
            "head": draw(a_person()),
            "spouse": draw(st.one_of(st.none(), a_person())),
            "dependent": draw(st.one_of(st.none(), a_person())),
        }

    @hypothesis.settings(max_examples=40, deadline=None, suppress_health_check=SLOW)
    @hypothesis.given(st.lists(household(), min_size=1, max_size=15))
    def test_premiums_subtracted_once(households):
        assert_premiums_subtracted_once(households)

    @hypothesis.settings(max_examples=40, deadline=None, suppress_health_check=SLOW)
    @hypothesis.given(
        st.lists(household(), min_size=1, max_size=15),
        st.sampled_from(["gambling_winnings", "financial_assistance"]),
        st.integers(min_value=1, max_value=600),
    )
    def test_exclusions(households, name, extra):
        assert_exclusion(households, name, extra)
