"""Property tests: South Carolina TANF gross earned and unearned income.

SC DSS TANF Policy Manual, Volume 67 (July 2026):

- Section 7.1 (PDF page 102): "Income is money received by a BG member (s)
  from any source."
- Section 7.7 (pages 107-120) counts Social Security at the gross amount
  (page 116), unemployment compensation (page 118), pensions (page 115),
  child support (page 108) and VA benefits (page 119), and counts interest,
  dividends and royalties with "Up to $400 per BG annually ... excluded.
  Income above $400 must be averaged over the period of the remaining 12
  months" (page 113). It excludes "the SSI recipient, his/her income"
  (page 117).
- Section 6.6 (pages 92-93) counts IRA and Keogh balances as resources, so
  a withdrawal is not income; a discharged debt is not money received.

For every benefit group, in a month:

1. Each member's sc_tanf_gross_unearned_income equals a reference written
   from the chart above, not from the model's parameter list: the member's
   counted sources, less a share of min(group interest and dividends,
   400 / 12) proportional to the member's interest and dividends. SSI
   recipients count nothing and take no share.
2. The group's total is its counted sources less min(group interest and
   dividends, 400 / 12), and no member's exclusion exceeds the member's own
   interest and dividends.
3. Retirement account withdrawals, discharged debt and wages never change
   unearned income (property 1 holds with them present).
4. sc_tanf_gross_earned_income is wages, or zero for an SSI recipient.
5. Raising the head's interest by d raises the group's unearned income by
   between 0 and d / 12: by exactly d / 12 when the group's interest and
   dividends already exceed the exclusion, and by 0 when the head receives
   SSI.

Each generated group is simulated twice in one vectorized simulation: as
drawn, and with the head's interest raised (property 5).
"""

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2025
MONTH = f"{YEAR}-01"
EXCLUSION = 400  # Section 7.7, page 113, per benefit group per year.
TOLERANCE = 0.01

# Sources the chart counts at the gross amount, in model input names.
COUNTED = [
    "social_security_retirement",
    "unemployment_compensation",
    "taxable_private_pension_income",
    "tax_exempt_private_pension_income",
    "child_support_received",
    "veterans_benefits",
]
INTEREST_AND_DIVIDENDS = [
    "taxable_interest_income",
    "tax_exempt_interest_income",
    "qualified_dividend_income",
    "non_qualified_dividend_income",
]
# Inputs that must not count as unearned income.
IGNORED = ["taxable_ira_distributions", "debt_relief"]
WAGES = "employment_income_before_lsr"
AMOUNT_INPUTS = [*COUNTED, *INTEREST_AND_DIVIDENDS, *IGNORED, WAGES]


def build_situation(groups):
    """One household, SPM unit, tax unit and family per group; each person
    is unmarried. Adults are 30 to 50 and children 1 to 17, and nobody is
    disabled, so the model computes no SSI; SSI receipt comes only from
    receives_ssi."""
    people, tax_units, spm_units, families, households = {}, {}, {}, {}, {}
    marital_units = {}
    for i, group in enumerate(groups):
        members = []
        for j, member in enumerate(group):
            name = f"person_{i}_{j}"
            person = {
                "age": {YEAR: member["age"]},
                "receives_ssi": {MONTH: member["ssi"]},
            }
            for variable in AMOUNT_INPUTS:
                person[variable] = {YEAR: member.get(variable, 0)}
            people[name] = person
            members.append(name)
            marital_units[f"marital_unit_{i}_{j}"] = {"members": [name]}
        tax_units[f"tax_unit_{i}"] = {"members": members}
        spm_units[f"spm_unit_{i}"] = {"members": members}
        families[f"family_{i}"] = {"members": members}
        households[f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "SC"},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "spm_units": spm_units,
        "families": families,
        "marital_units": marital_units,
        "households": households,
    }


def raise_head_interest(group, d):
    raised = [dict(member) for member in group]
    raised[0]["taxable_interest_income"] = (
        raised[0].get("taxable_interest_income", 0) + d
    )
    return raised


def reference(group):
    """Monthly gross unearned and earned income per member, from the
    manual."""
    counted, idr, earned = [], [], []
    for member in group:
        keep = 0 if member["ssi"] else 1
        member_idr = sum(member.get(v, 0) for v in INTEREST_AND_DIVIDENDS)
        member_counted = sum(member.get(v, 0) for v in COUNTED) + member_idr
        counted.append(keep * member_counted / 12)
        idr.append(keep * member_idr / 12)
        earned.append(keep * member.get(WAGES, 0) / 12)
    group_idr = sum(idr)
    exclusion = min(group_idr, EXCLUSION / 12)
    unearned = [
        c - (exclusion * x / group_idr if group_idr > 0 else 0)
        for c, x in zip(counted, idr)
    ]
    return unearned, earned, exclusion


def run(groups, raises):
    """Simulate each group as drawn and with the head's interest raised.
    Return per-member values for both copies."""
    doubled = groups + [raise_head_interest(g, d) for g, d in zip(groups, raises)]
    sim = Simulation(situation=build_situation(doubled))
    unearned = np.asarray(sim.calculate("sc_tanf_gross_unearned_income", MONTH))
    earned = np.asarray(sim.calculate("sc_tanf_gross_earned_income", MONTH))
    ssi = np.asarray(sim.calculate("sc_tanf_ssi_recipient", MONTH))
    sizes = [len(g) for g in doubled]
    bounds = np.cumsum([0, *sizes])
    split = lambda a: [a[bounds[k] : bounds[k + 1]] for k in range(len(doubled))]
    n = len(groups)
    u, e, s = split(unearned), split(earned), split(ssi)
    return (u[:n], e[:n], s[:n]), (u[n:], e[n:], s[n:])


def check(groups, raises):
    (unearned, earned, ssi), (raised_unearned, _, _) = run(groups, raises)
    for k, group in enumerate(groups):
        expected_unearned, expected_earned, exclusion = reference(group)
        context = {"group": group}
        # Property 1 and 3: the reference from the manual.
        assert unearned[k] == pytest.approx(expected_unearned, abs=TOLERANCE), context
        # Property 4.
        assert earned[k] == pytest.approx(expected_earned, abs=TOLERANCE), context
        assert list(ssi[k]) == [bool(m["ssi"]) for m in group], context
        # Property 2: group conservation and per-member bounds.
        counted = [
            0
            if m["ssi"]
            else sum(m.get(v, 0) for v in COUNTED + INTEREST_AND_DIVIDENDS) / 12
            for m in group
        ]
        assert unearned[k].sum() == pytest.approx(
            sum(counted) - exclusion, abs=TOLERANCE
        ), context
        for member, value, member_counted in zip(group, unearned[k], counted):
            member_idr = (
                0
                if member["ssi"]
                else sum(member.get(v, 0) for v in INTEREST_AND_DIVIDENDS) / 12
            )
            assert -TOLERANCE <= member_counted - value <= member_idr + TOLERANCE
        # Property 5: monotone in the head's interest.
        change = raised_unearned[k].sum() - unearned[k].sum()
        d = raises[k] / 12
        assert -TOLERANCE <= change <= d + TOLERANCE, context
        group_idr = sum(
            0 if m["ssi"] else sum(m.get(v, 0) for v in INTEREST_AND_DIVIDENDS) / 12
            for m in group
        )
        if group[0]["ssi"]:
            assert change == pytest.approx(0, abs=TOLERANCE), context
        elif group_idr >= EXCLUSION / 12:
            assert change == pytest.approx(d, abs=TOLERANCE), context


def test_worked_example():
    """Integration Case 9's benefit group, from the manual: child support
    3,600, interest 1,000, and a child's Social Security 4,800 a year."""
    groups = [
        [
            {
                "age": 30,
                "ssi": False,
                "child_support_received": 3_600,
                "taxable_interest_income": 1_000,
            },
            {"age": 9, "ssi": False, "social_security_retirement": 4_800},
            {"age": 6, "ssi": False},
        ]
    ]
    (unearned, _, _), _ = run(groups, [0])
    # 300 + (1,000 - 400) / 12 = 350 for the parent; 400 for the child.
    assert unearned[0] == pytest.approx([350, 400, 0], abs=TOLERANCE)


try:
    import hypothesis
    import hypothesis.strategies as st
except ImportError:  # pragma: no cover
    hypothesis = None

if hypothesis is not None:
    SLOW = [hypothesis.HealthCheck.too_slow]

    def amount(high):
        return st.one_of(st.just(0), st.integers(min_value=1, max_value=high))

    @st.composite
    def member(draw, age):
        return {
            "age": age,
            "ssi": draw(st.booleans()),
            "social_security_retirement": draw(amount(24_000)),
            "unemployment_compensation": draw(amount(15_000)),
            "taxable_private_pension_income": draw(amount(10_000)),
            "tax_exempt_private_pension_income": draw(amount(5_000)),
            "child_support_received": draw(amount(8_000)),
            "veterans_benefits": draw(amount(12_000)),
            "taxable_interest_income": draw(amount(3_000)),
            "tax_exempt_interest_income": draw(amount(1_000)),
            "qualified_dividend_income": draw(amount(2_000)),
            "non_qualified_dividend_income": draw(amount(1_000)),
            "taxable_ira_distributions": draw(amount(20_000)),
            "debt_relief": draw(amount(5_000)),
            "employment_income_before_lsr": draw(amount(30_000)),
        }

    @st.composite
    def group(draw):
        head = draw(member(draw(st.integers(min_value=30, max_value=50))))
        children = draw(
            st.lists(
                member(draw(st.integers(min_value=1, max_value=17))),
                min_size=0,
                max_size=3,
            )
        )
        return [head, *children]

    @hypothesis.settings(
        max_examples=15, derandomize=True, deadline=None, suppress_health_check=SLOW
    )
    @hypothesis.given(
        st.lists(
            st.tuples(group(), st.integers(min_value=1, max_value=5_000)),
            min_size=1,
            max_size=8,
        )
    )
    def test_properties(cases):
        groups = [g for g, _ in cases]
        raises = [d for _, d in cases]
        check(groups, raises)
