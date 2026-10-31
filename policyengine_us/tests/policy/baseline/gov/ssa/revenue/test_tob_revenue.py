"""Generated chapter 1 TOB differentials and branch cache isolation.

Policy examples and independent tax calculations live in the variable YAML
files. Python is needed to quantify the split invariants over generated
inputs and to exercise calculation order on an already populated cache.
Each generated batch combines eight income/donation draws with fixed
boundary and signed-allocation witnesses. Five filing profiles cover
single, joint, separate living together, separate living apart, and an
elderly single person electing to itemize. Cash gifts and tax-exempt
interest exercise binding charitable limits and elderly-credit changes.
Charitable gifts are the sole itemized deductions; deductible medical
expenses (including Medicare premiums) and state/local taxes are excluded.
One vectorized simulation shares the expensive counterfactual setup across
the batch. Joint benefits and interest are divided between spouses to
exercise tax-unit aggregation. Fresh, unbranched simulations independently
override taxable benefits at zero, pre-1993 and current-law inclusion.
They share unchanged policy, with separate populations, inputs and caches.
Elderly single/joint NIIT threshold crossings and working families with
children ensure that excluding NIIT and refundable credits is observable.
"""

from copy import deepcopy
from itertools import product

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation


PROFILES = (
    ("SINGLE", False, False),
    ("JOINT", True, False),
    ("SEPARATE", True, False),
    ("SEPARATE", False, False),
    ("SINGLE", False, True),
)
# Keep the former standalone Hypothesis examples in each vectorized batch,
# avoiding three additional full-model constructions. The last two cases
# release charitable deductions and elderly credits as inclusion rises;
# they cover negative OASDI and negative HI without the MFS credit base.
FIXED_CASES = (
    (20_000, 30_000, 0, 0),
    (0, 0, 0, 0),
    (60_000, 300_000, 0, 0),
    (1_000, 11_500, 20_000, 20_000),
    (1_000, 11_500, 23_000, 20_000),
)
REVENUE_VARIABLES = (
    "tob_revenue_oasdi",
    "tob_revenue_medicare_hi",
    "tob_revenue_total",
)


def simulation(
    cases,
    age,
    year,
    force_itemization=True,
    niit_gap=None,
    credit_cases=(),
    payroll_tax=None,
):
    situation = {
        entity: {}
        for entity in (
            "people",
            "tax_units",
            "households",
            "marital_units",
            "spm_units",
            "families",
        )
    }
    profiles = [(case, profile, age) for case, profile in product(cases, PROFILES)]
    if niit_gap is not None:
        for filing_status, threshold in (("SINGLE", 200_000), ("JOINT", 250_000)):
            profile = (filing_status, False, False)
            # No-inclusion MAGI is below the threshold; $34,000 of current
            # inclusion crosses it for every generated gap. Keep a second
            # elderly unit comfortably below the threshold as a control.
            profiles.extend(
                (
                    ((40_000, threshold - niit_gap, 0, 0), profile, 70),
                    ((40_000, 50_000, 0, 0), profile, 70),
                )
            )
    for i, (case, profile, case_age) in enumerate(profiles):
        benefits, interest, exempt_interest, donations = case
        filing_status, cohabitating, itemizes = profile
        joint = filing_status == "JOINT"
        members = [f"head{i}"] + ([f"spouse{i}"] if joint else [])
        for j, member in enumerate(members):
            situation["people"][member] = {
                "age": {year: 67 if itemizes else case_age},
                "tax_unit_role_input": {year: "HEAD" if j == 0 else "SPOUSE"},
                "social_security": {year: benefits / len(members)},
                "taxable_interest_income": {year: interest / len(members)},
                "tax_exempt_interest_income": {year: exempt_interest / len(members)},
                "charitable_cash_donations": {year: donations / len(members)},
            }
        situation["tax_units"][f"tax_unit{i}"] = {
            "members": members,
            "filing_status": {year: filing_status},
            "cohabitating_spouses": {year: cohabitating},
            "itemized_medical_expenses": {year: 0},
            "salt_deduction": {year: 0},
        }
        if force_itemization:
            situation["tax_units"][f"tax_unit{i}"]["tax_unit_itemizes"] = {
                year: itemizes
            }
        situation["households"][f"household{i}"] = {
            "members": members,
            "state_name": {year: "TX"},
        }
        # Missing group entities default to one group containing everyone,
        # so define each explicitly to keep these households independent.
        for entity in ("marital_units", "spm_units", "families"):
            situation[entity][f"unit{i}"] = {"members": members}
        # These childless units do not participate in TANF. Supplying this
        # avoids unrelated monthly benefit calculations in tax branches.
        situation["spm_units"][f"unit{i}"]["takes_up_tanf_if_eligible"] = {year: False}
    for i, (benefits, earnings, children) in enumerate(credit_cases):
        head = f"credit_head{i}"
        dependents = [f"credit_child{i}_{j}" for j in range(children)]
        members = [head, *dependents]
        situation["people"][head] = {
            "age": {year: 40},
            "is_disabled": {year: True},
            "tax_unit_role_input": {year: "HEAD"},
            "social_security": {year: benefits},
            "employment_income": {year: earnings},
        }
        for child in dependents:
            situation["people"][child] = {
                "age": {year: 8},
                "tax_unit_role_input": {year: "DEPENDENT"},
            }
        for entity in ("tax_units", "households", "spm_units", "families"):
            situation[entity][f"credit_unit{i}"] = {"members": members}
        situation["tax_units"][f"credit_unit{i}"].update(
            {
                "filing_status": {year: "HEAD_OF_HOUSEHOLD"},
                "tax_unit_itemizes": {year: False},
                "itemized_medical_expenses": {year: 0},
                "salt_deduction": {year: 0},
            }
        )
        situation["households"][f"credit_unit{i}"]["state_name"] = {year: "TX"}
        situation["spm_units"][f"credit_unit{i}"]["takes_up_tanf_if_eligible"] = {
            year: False
        }
        # A child has a separate marital unit, rather than joining the parent.
        for member in members:
            situation["marital_units"][member] = {"members": [member]}
    if payroll_tax is not None:
        # Pair every input with an otherwise identical payroll-tax case in
        # the same vectorized batch. This tests all three TOB variables with
        # unchanged production branch setup and separate household inputs.
        for entity, records in situation.items():
            for name, inputs in tuple(records.items()):
                duplicate = deepcopy(inputs)
                if "members" in duplicate:
                    duplicate["members"] = [
                        f"{member}_with_payroll" for member in duplicate["members"]
                    ]
                if entity == "tax_units":
                    duplicate["unreported_payroll_tax"] = {year: payroll_tax}
                records[f"{name}_with_payroll"] = duplicate
    return Simulation(situation=situation)


def fresh_simulation(sim, year, taxable_ss):
    """Share only policy: never borrow branches or calculated arrays."""
    situation = deepcopy(sim.situation_input)
    for i, tax_unit in enumerate(situation["tax_units"].values()):
        tax_unit["tax_unit_taxable_social_security"] = {year: float(taxable_ss[i])}
    return Simulation(tax_benefit_system=sim.tax_benefit_system, situation=situation)


def independent_tax_states(sim, year):
    """Read tax components at explicit inclusion inputs, without TOB formulas."""
    current_ss = sim.calculate("tax_unit_taxable_social_security", year)
    pre_1993_ss = sim.calculate("tax_unit_taxable_social_security_pre_1993", year)
    states = []
    for inclusion in (np.zeros_like(current_ss), pre_1993_ss, current_ss):
        independent = fresh_simulation(sim, year, taxable_ss=inclusion)
        components = {
            name: np.asarray(independent.calculate(name, year), dtype=np.float64)
            for name in (
                "income_tax_chapter_1",
                "income_tax_before_refundable_credits",
                "income_tax",
                "net_investment_income_tax",
                "income_tax_refundable_credits",
                "unreported_payroll_tax",
                "eitc",
                "refundable_ctc",
            )
        }
        assert not independent.branches
        np.testing.assert_allclose(
            components["income_tax_chapter_1"],
            components["income_tax_before_refundable_credits"]
            - components["net_investment_income_tax"]
            - components["unreported_payroll_tax"],
            rtol=0,
            atol=0.01,
        )
        states.append(components)
    return states


def check_independent_differentials(sim, year, result):
    zero, pre_1993, current = independent_tax_states(sim, year)
    zero_payroll = zero["unreported_payroll_tax"] == 0
    for state, name in (
        (pre_1993, "tob_revenue_oasdi"),
        (current, "tob_revenue_total"),
    ):
        delta = {component: state[component] - zero[component] for component in state}
        # The oracle never runs a production TOB branch or neutralizes a
        # variable. It calculates chapter 1 tax with explicit inclusion inputs.
        np.testing.assert_allclose(
            result[name], delta["income_tax_chapter_1"], rtol=0, atol=0.01
        )
        # Adding payroll tax before differencing float32 totals can amplify
        # rounding. Use the zero-payroll partners for these corrected totals;
        # every profile also has payroll invariance and all-unit chapter 1
        # differentials/component identities checked independently.
        np.testing.assert_allclose(
            result[name][zero_payroll],
            (
                delta["income_tax_before_refundable_credits"]
                - delta["net_investment_income_tax"]
            )[zero_payroll],
            rtol=0,
            atol=0.01,
        )
        np.testing.assert_allclose(
            result[name][zero_payroll],
            (
                delta["income_tax"]
                - delta["net_investment_income_tax"]
                + delta["income_tax_refundable_credits"]
            )[zero_payroll],
            rtol=0,
            atol=0.01,
        )
    # Guard against a generator that silently stops reaching the exclusions.
    assert np.any(
        (zero["net_investment_income_tax"] == 0)
        & (current["net_investment_income_tax"] > 0)
    )
    assert np.any(current["net_investment_income_tax"] == 0)
    assert np.any(current["eitc"] < zero["eitc"])
    assert np.any(current["refundable_ctc"] < zero["refundable_ctc"])


def check_invariants(sim, year, order=REVENUE_VARIABLES):
    taxable_ss = sim.calculate("tax_unit_taxable_social_security", year).copy()
    old_law_ss = sim.calculate("tax_unit_taxable_social_security_pre_1993", year)
    result = {name: sim.calculate(name, year).copy() for name in order}
    oasdi, hi, total = (result[name] for name in REVENUE_VARIABLES)
    # Float32 tax subtraction can lose a few mills at the upper generated
    # income bound; no policy difference of a cent is tolerated.
    tolerance = 0.01
    np.testing.assert_allclose(oasdi + hi, total, rtol=0, atol=tolerance)
    # Revenue differences are signed: deductions and credits can make tax
    # fall as inclusion rises. Equal counterfactual inclusions still imply
    # equal taxes, even for those households.
    np.testing.assert_allclose(oasdi[old_law_ss == 0], 0, rtol=0, atol=tolerance)
    np.testing.assert_allclose(hi[old_law_ss == taxable_ss], 0, rtol=0, atol=tolerance)
    assert np.all(old_law_ss >= -tolerance)
    assert np.all(old_law_ss <= taxable_ss + tolerance)
    np.testing.assert_array_equal(
        sim.calculate("tax_unit_taxable_social_security", year), taxable_ss
    )
    # The formulas remove their temporary branches after calculation.
    assert not {
        "oasdi_no_ss",
        "oasdi_capped",
        "oasdi_pre_1993",
        "oasdi_old_law",
        "hi_capped",
        "tob_calc",
    }.intersection(sim.branches)
    return result


# Each generated draw exercises 73 pairs of tax units in three counterfactuals.
# Batching increases generated household coverage while reducing full-model
# branch clones; each draw still owns an independent simulation and caches.
@settings(max_examples=2, derandomize=True, deadline=None)
@given(
    cases=st.lists(
        st.tuples(
            st.integers(min_value=0, max_value=60_000),
            st.integers(min_value=0, max_value=300_000),
            st.integers(min_value=0, max_value=100_000),
            st.integers(min_value=0, max_value=300_000),
        ),
        min_size=8,
        max_size=8,
    ),
    age=st.sampled_from([60, 70]),
    niit_gap=st.integers(min_value=1, max_value=30_000),
    credit_cases=st.lists(
        st.tuples(
            st.integers(min_value=10_000, max_value=40_000),
            st.integers(min_value=25_000, max_value=40_000),
            st.integers(min_value=1, max_value=3),
        ),
        min_size=2,
        max_size=2,
    ),
    payroll_tax=st.integers(min_value=1, max_value=25_000),
)
def test_generated_tob_split_invariants(
    cases, age, niit_gap, credit_cases, payroll_tax
):
    # The elderly-credit witnesses remain taxable in 2024. The 2026 senior
    # deduction can eliminate their tax; that year's counterfactual/cache
    # behavior is covered independently by the test below.
    year = 2024
    sim = simulation(
        [*cases, *FIXED_CASES],
        age,
        year,
        niit_gap=niit_gap,
        credit_cases=[*credit_cases, (40_000, 30_000, 1), (20_000, 30_000, 2)],
        payroll_tax=payroll_tax,
    )
    result = check_invariants(sim, year)
    for name in REVENUE_VARIABLES:
        without_payroll, with_payroll = np.split(result[name], 2)
        np.testing.assert_array_equal(with_payroll, without_payroll)
    check_independent_differentials(sim, year, result)
    # Verify that the population actually exercises both kinds of signed
    # allocation rather than passing only on non-negative households.
    assert np.any(result["tob_revenue_oasdi"] < 0)
    assert np.any(result["tob_revenue_medicare_hi"] < 0)


def test_tob_split_preserves_inputs_and_cached_current_law_tax_in_either_order():
    year = 2026
    # Keep itemization endogenous here so branches must also invalidate and
    # recompute its cached choice, rather than preserve a fixed input.
    sim = simulation(FIXED_CASES, 70, year, force_itemization=False)
    # Populate the cache before creating counterfactual branches. If the
    # branches keep calculated AGI or tax arrays, the split can become zero.
    names = (
        "social_security",
        "taxable_interest_income",
        "tax_exempt_interest_income",
        "charitable_cash_donations",
        "tax_unit_itemizes",
        "itemized_medical_expenses",
        "salt_deduction",
        "tax_unit_taxable_social_security",
        "adjusted_gross_income",
        "income_tax",
    )
    original = {name: sim.calculate(name, year).copy() for name in names}
    first = check_invariants(sim, year)
    for name in REVENUE_VARIABLES:
        sim.delete_arrays(name)
    # Starting with HI also exercises HI -> total/OASDI dependencies.
    reverse = check_invariants(
        sim,
        year,
        ("tob_revenue_medicare_hi", "tob_revenue_total", "tob_revenue_oasdi"),
    )
    for name in REVENUE_VARIABLES:
        np.testing.assert_array_equal(reverse[name], first[name])
    for name in names:
        np.testing.assert_array_equal(sim.calculate(name, year), original[name])
