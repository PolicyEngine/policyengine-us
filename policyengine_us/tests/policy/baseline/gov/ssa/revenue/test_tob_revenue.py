"""Generated chapter 1 TOB differentials, branch cache isolation and reforms.

Policy examples and independent tax calculations live in the variable YAML
files, except the three parameter reforms that test actual inclusion's cap
on the old-law inclusion. Core's YAML runner keeps a cloned policy system
for each distinct parameter reform until its process ends, and in CI the
YAML file holding those three peaked at 8,244 MB. The last test here runs
them in turn on one private copy of the policy and restores its parameters
between them. Python is also
needed to quantify the split invariants over generated inputs and to
exercise calculation order on an already populated cache.
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
from functools import reduce
import gc
from itertools import product

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st
from policyengine_core.reforms import set_parameter

from policyengine_us import Simulation
from policyengine_us.spm import clone_spm_system, copy_parameter_nodes
from policyengine_us.system import system


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
    # OASDI caps old-law inclusion at actual inclusion. At current law the
    # pre-1993 amount never exceeds actual inclusion, with no tolerance, so
    # the cap returns the pre-1993 amount exactly and changes nothing. The
    # independent pre-1993 differentials confirm the OASDI values.
    assert np.all(old_law_ss <= taxable_ss)
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


# Reform scoring: actual inclusion caps the old-law inclusion in the
# OASDI/HI split (ruling us:tob-oasdi-old-law-bound).
#
# Every case reuses the 2026 single retiree from tob_revenue_oasdi.yaml:
# age 70, $20,000 benefits and $30,000 taxable interest. At current law that
# unit includes $9,600 against a $7,500 pre-1993 amount, with OASDI $769,
# HI $252 and total $1,021. The pre-1993 amount reads its own
# gov.ssa.revenue.pre_1993 parameters, so it stays $7,500 under each reform
# below.
#
# Deductions are $16,100 + $2,050 + $6,000 = $24,150 in every counterfactual,
# and taxable income is $30,000 + inclusion - $24,150. Tax is 10% up to
# $12,400, then 12%. Tax with no inclusion is 10% * $5,850 = $585. Nontaxable
# benefits stay above the $5,000 elderly-credit base, or AGI phases the
# credit out, so the credit is zero in every counterfactual.
#
# OASDI + HI = total in each case.
REFORM_YEAR = 2026
RETIREE = {
    "people": {
        "retiree": {
            "age": {REFORM_YEAR: 70},
            "social_security": {REFORM_YEAR: 20_000},
            "taxable_interest_income": {REFORM_YEAR: 30_000},
        }
    },
    "tax_units": {
        "tax_unit": {
            "members": ["retiree"],
            "filing_status": {REFORM_YEAR: "SINGLE"},
        }
    },
    "spm_units": {
        "spm_unit": {
            "members": ["retiree"],
            "takes_up_tanf_if_eligible": {REFORM_YEAR: False},
        }
    },
    "households": {"household": {"members": ["retiree"]}},
}
# Every parameter leaf that any case below reforms.
REFORMED_LEAVES = (
    "gov.irs.social_security.taxability.rate.base.benefit_cap",
    "gov.irs.social_security.taxability.rate.base.excess",
    "gov.irs.social_security.taxability.rate.additional.benefit_cap",
    "gov.irs.social_security.taxability.rate.additional.bracket",
    "gov.irs.social_security.taxability.rate.additional.excess",
    "gov.irs.social_security.taxability.threshold.base.main.SINGLE",
    "gov.irs.social_security.taxability.threshold.adjusted_base.main.SINGLE",
    "gov.irs.social_security.taxability.combined_income_ss_fraction",
)
# Each case: its name, its parameter inputs and its expected outputs.
REFORM_CASES = (
    (
        "Repealing benefit taxation leaves OASDI, HI and the total at zero",
        {
            "gov.irs.social_security.taxability.rate.base.benefit_cap": 0,
            "gov.irs.social_security.taxability.rate.base.excess": 0,
            "gov.irs.social_security.taxability.rate.additional.benefit_cap": 0,
            "gov.irs.social_security.taxability.rate.additional.bracket": 0,
            "gov.irs.social_security.taxability.rate.additional.excess": 0,
        },
        {
            "tax_unit_combined_income_for_social_security_taxability": 40_000,
            # Old law: min(50% * $20,000, 50% * ($40,000 - $25,000)) = $7,500.
            "tax_unit_taxable_social_security_pre_1993": 7_500,
            # Every section 86 rate is zero, so the unit includes nothing.
            "tax_unit_taxable_social_security": 0,
            # The cap gives old-law inclusion min($7,500, $0) = $0, so all three
            # branches tax $0 of benefits. Without the cap OASDI would be
            # $1,354 - $585 = $769 and HI -$769 on a $0 total.
            "tob_revenue_oasdi": 0,
            "tob_revenue_medicare_hi": 0,
            "tob_revenue_total": 0,
        },
    ),
    (
        "Raised thresholds put inclusion below the old-law amount, so OASDI "
        "takes it all",
        {
            "gov.irs.social_security.taxability.threshold.base.main.SINGLE": 30_000,
            "gov.irs.social_security.taxability.threshold.adjusted_base.main.SINGLE": 44_000,
        },
        {
            "tax_unit_combined_income_for_social_security_taxability": 40_000,
            "tax_unit_taxable_social_security_pre_1993": 7_500,
            # Provisional income of $40,000 falls between the $30,000 base and
            # the $44,000 adjusted base, so only the first tier applies:
            # min(50% * $20,000, 50% * ($40,000 - $30,000)) = $5,000.
            # That is positive and below the $7,500 old-law amount.
            "tax_unit_taxable_social_security": 5_000,
            # Old-law inclusion = min($7,500, $5,000) = $5,000, the actual
            # inclusion. Taxable income with $5,000 included =
            # $35,000 - $24,150 = $10,850, all in the 10% bracket, so
            # tax = $1,085.
            # Total = OASDI = $1,085 - $585 = $500; HI = $500 - $500 = $0.
            # Without the cap OASDI would be $1,354 - $585 = $769 and HI -$269.
            "tob_revenue_oasdi": 500,
            "tob_revenue_medicare_hi": 0,
            "tob_revenue_total": 500,
        },
    ),
    (
        "A reform that raises inclusion keeps the pre-1993 OASDI share and "
        "gives HI the rest",
        # The same override as tax_unit_taxable_social_security_pre_1993.yaml.
        {"gov.irs.social_security.taxability.combined_income_ss_fraction": 0.85},
        {
            # Current-law provisional income = $30,000 + 85% * $20,000
            # = $47,000.
            "tax_unit_combined_income_for_social_security_taxability": 47_000,
            "tax_unit_taxable_social_security_pre_1993": 7_500,
            # min(85% * ($47,000 - $34,000) + min($10,000, $4,500),
            # 85% * $20,000) = min($11,050 + $4,500, $17,000) = $15,550,
            # above the $9,600 at current law.
            "tax_unit_taxable_social_security": 15_550,
            # Old-law inclusion = min($7,500, $15,550) = $7,500, as at current
            # law. Taxable income $13,350 / $21,400 with old-law / reform
            # inclusion; tax $1,240 + 12% * $950 = $1,354 and
            # $1,240 + 12% * $9,000 = $2,320.
            # OASDI = $1,354 - $585 = $769, its current-law value.
            # HI = $2,320 - $1,354 = $966; total = $2,320 - $585 = $1,735.
            "tob_revenue_oasdi": 769,
            "tob_revenue_medicare_hi": 966,
            "tob_revenue_total": 1_735,
        },
    ),
)


def parameter_history(parameter):
    return tuple((entry.instant_str, entry.value) for entry in parameter.values_list)


def test_reforms_cap_old_law_inclusion_at_actual_inclusion():
    """Run each reform case in turn on one private copy of the shared policy.

    As YAML, each case's parameter inputs built and kept one more cloned
    system. Here every case shares one private copy: it starts from current
    law on all eight reformed leaves and applies its inputs exactly as Core's
    YAML runner does. The shared system's leaves must be unchanged afterwards,
    whether or not a case failed.
    """
    instant = f"{REFORM_YEAR}-01-01"
    shared = {path: system.parameters.get_child(path) for path in REFORMED_LEAVES}
    shared_lists = {path: leaf.values_list for path, leaf in shared.items()}
    shared_histories = {path: parameter_history(leaf) for path, leaf in shared.items()}
    current_law = {path: leaf(instant) for path, leaf in shared.items()}
    # The copy owns every node and each leaf's list of dated values, and
    # borrows the entries in those lists rather than rebuilding them as a
    # full clone does. Parameter.update replaces a leaf's list and never
    # edits an entry, so no write here reaches the shared system.
    policy = clone_spm_system(
        system, parameters=copy_parameter_nodes(system.parameters)
    )
    try:
        leaves = {path: policy.parameters.get_child(path) for path in REFORMED_LEAVES}
        for path, leaf in leaves.items():
            assert leaf is not shared[path]
            assert leaf.values_list is not shared_lists[path]
            assert parameter_history(leaf) == shared_histories[path]
        # The copy's original lists hold current law, so they restore it.
        current_law_lists = {path: leaf.values_list for path, leaf in leaves.items()}
        for name, reform, expected in REFORM_CASES:
            for path, leaf in leaves.items():
                leaf.values_list = list(current_law_lists[path])
                # Assigning the list skips the cache clearing update does.
                leaf.parent.clear_parent_cache()
            for path, value in reform.items():
                # The modifier Core's YAML runner applies for a parameter input.
                set_parameter(path, value, period="year:2000:40", return_modifier=True)(
                    policy.parameters
                )
            # Updates clear each node's cache from the leaf up to the root, but
            # not the system's own cache of parameters at each instant.
            policy._parameters_at_instant_cache.clear()
            # A new simulation of the same situation, built after the reform,
            # holds no calculated value from an earlier case.
            simulation = Simulation(
                tax_benefit_system=policy, situation=deepcopy(RETIREE)
            )
            try:
                parameters = simulation.tax_benefit_system.parameters(instant)
                for path in REFORMED_LEAVES:
                    assert reduce(getattr, path.split("."), parameters) == (
                        reform.get(path, current_law[path])
                    ), f"{name}: {path}"
                for variable, value in expected.items():
                    np.testing.assert_allclose(
                        simulation.calculate(variable, REFORM_YEAR),
                        value,
                        rtol=0,
                        atol=0.01,
                        err_msg=f"{name}: {variable}",
                    )
            finally:
                # Free this case's simulation and the branch systems its TOB
                # formulas discarded.
                del simulation
                gc.collect()
    finally:
        del policy
        gc.collect()
        for path, leaf in shared.items():
            assert system.parameters.get_child(path) is leaf
            assert leaf.values_list is shared_lists[path]
            assert parameter_history(leaf) == shared_histories[path]
