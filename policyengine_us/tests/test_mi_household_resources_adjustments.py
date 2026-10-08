"""Property tests: MI-1040CR line 30 in Michigan household resources.

Line 30 is "total adjustments from your U.S. Form 1040, Schedule 1" (2025
MI-1040 book, page 32): the Schedule 1 Part II adjustments to income, which
gov.states.mi.tax.income.household_resources_adjustments lists. The federal
above-the-line list, gov.irs.ald.deductions, also holds items that are not
Part II adjustments:

- loss_ald: business, rental and capital losses, which are income items
  (lines 16, 17 and 19);
- us_bonds_for_higher_ed, qualified_adoption_assistance_expense,
  specified_possession_income and puerto_rico_income: income that IRC 135,
  137, 931 and 933 exclude from gross income. Total household resources are
  "AGI ... plus all income exempt or excluded from AGI" (page 26), and line 15
  is "All interest and dividend income (including nontaxable interest)".

Because the federal list subtracts each exclusion from gross income, the
excluded amount is entered in the income it comes from (savings bond interest
in interest income, adoption benefits and possession income in wages, as these
tests do). Line 30 must not take it back out.

Invariants, for every input:

1. The Michigan list is exactly the Schedule 1 Part II adjustments named in
   SCHEDULE_1_ADJUSTMENTS below (written from the 2025 Schedule 1). Every
   federal above-the-line deduction from 2021 on is either one of them or one
   of the five items above, never both, and each is a federal above-the-line
   deduction.
2. mi_household_resources = max(0, wages + all interest + max(0, Schedule C)
   - Schedule 1 adjustments - premiums), where the adjustments are the
   SCHEDULE_1_ADJUSTMENTS the federal list deducts. Their amounts are read
   from the model one by one, since the self-employment tax and student loan
   interest deductions depend on income; which variables count comes from
   this file, not from the parameter. The reference subtracts none of the
   exclusions. This is a differential test against a reference written from
   the form.
3. The exclusions reach household resources only through the student loan
   interest deduction, whose modified AGI applies sections 135 and 137
   (IRC 221(b)(2)(C)). Compared with the same household without exclusions,
   with D the change in that deduction: household resources are
   max(0, resources without - D) (equal when D = 0), and federal AGI is
   lower by the exclusions plus D.
4. Line 30 follows the federal list: a reform that removes the early
   withdrawal penalty and the IRA deduction from gov.irs.ald.deductions
   removes them from line 30, and removing an exclusion from the federal
   list does not put it on line 30.

The model computes in single precision, so a comparison allows one cent or
eight float32 spacings at the household's total absolute amount, whichever is
larger.
"""

import itertools

import numpy as np
import pytest

from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.system import system

try:
    import hypothesis
    import hypothesis.strategies as st
except ImportError:  # Hypothesis is a dev extra.
    hypothesis = None

YEAR = 2025
TOLERANCE = 0.01

# Federal above-the-line deductions that are U.S. Schedule 1 Part II
# adjustments (2025 Schedule 1 line), written from the form.
SCHEDULE_1_ADJUSTMENTS = {
    "educator_expense_ald": "11",
    "health_savings_account_ald": "13",
    "self_employment_tax_ald": "15",
    "self_employed_pension_contribution_ald": "16",
    "self_employed_health_insurance_ald": "17",
    "early_withdrawal_penalty": "18",
    "alimony_expense_ald": "19a",
    "traditional_ira_contributions": "20",
    "student_loan_interest_ald": "21",
}
# Federal above-the-line deductions that are not Schedule 1 Part II
# adjustments.
NOT_SCHEDULE_1_ADJUSTMENTS = {
    "loss_ald",
    "us_bonds_for_higher_ed",
    "qualified_adoption_assistance_expense",
    "specified_possession_income",
    "puerto_rico_income",
}
PERSON_EXCLUSIONS = ["us_bonds_for_higher_ed", "qualified_adoption_assistance_expense"]
UNIT_EXCLUSIONS = ["specified_possession_income", "puerto_rico_income"]
PERSON_INPUTS = [
    "employment_income_before_lsr",
    "taxable_interest_income",
    "tax_exempt_interest_income",
    "self_employment_income",
    *PERSON_EXCLUSIONS,
    "early_withdrawal_penalty",
    "traditional_ira_contributions",
    "student_loan_interest",
    "health_insurance_premiums",
]


def build_situation(households):
    """One single-person Michigan tax unit per household."""
    people, tax_units, households_out = {}, {}, {}
    for i, h in enumerate(households):
        name = f"person_{i}"
        people[name] = {"age": {YEAR: 45}}
        for variable in PERSON_INPUTS:
            people[name][variable] = {YEAR: h[variable]}
        # Set on every unit: a variable input for some units gives the
        # others its default value, not its formula.
        tax_units[f"tax_unit_{i}"] = {
            "members": [name],
            **{variable: {YEAR: h[variable]} for variable in UNIT_EXCLUSIONS},
        }
        households_out[f"household_{i}"] = {
            "members": [name],
            "state_code": {YEAR: "MI"},
        }
    return {"people": people, "tax_units": tax_units, "households": households_out}


def without_federal_deductions(removed):
    """A reform that removes deductions from gov.irs.ald.deductions."""

    class reform(Reform):
        def apply(self):
            def modify(parameters):
                deductions = parameters.gov.irs.ald.deductions
                values = [d for d in deductions(f"{YEAR}-01-01") if d not in removed]
                deductions.update(
                    start=instant(f"{YEAR}-01-01"),
                    stop=instant(f"{YEAR}-12-31"),
                    value=values,
                )
                return parameters

            self.modify_parameters(modify)

    return reform


def calculate(households, reform=None):
    simulation = Simulation(situation=build_situation(households), reform=reform)
    results = {
        v: np.asarray(simulation.calculate(v, YEAR))
        for v in ["mi_household_resources", "adjusted_gross_income"]
    }
    # Each Schedule 1 adjustment the federal list deducts, per tax unit.
    federal = simulation.tax_benefit_system.parameters.gov.irs.ald.deductions(
        f"{YEAR}-01-01"
    )
    results["adjustments"] = {
        d: np.asarray(simulation.calculate(d, YEAR, map_to="tax_unit"))
        for d in SCHEDULE_1_ADJUSTMENTS
        if d in federal
    }
    results["student_loan_interest_ald"] = np.asarray(
        simulation.calculate("student_loan_interest_ald", YEAR, map_to="tax_unit")
    )
    return results


def tolerance(h):
    """One cent, or eight float32 spacings at the household's total absolute
    amount."""
    scale = sum(abs(h[v]) for v in [*PERSON_INPUTS, *UNIT_EXCLUSIONS])
    return max(TOLERANCE, 8 * float(np.spacing(np.float32(scale))))


def reference(h, line_30):
    """MI-1040CR line 33, total household resources, from the form."""
    line_14 = h["employment_income_before_lsr"]
    # "All interest and dividend income (including nontaxable interest)",
    # savings bond interest excluded under section 135 included.
    line_15 = h["taxable_interest_income"] + h["tax_exempt_interest_income"]
    line_16 = max(0, h["self_employment_income"])
    line_31 = h["health_insurance_premiums"]
    return max(0, line_14 + line_15 + line_16 - line_30 - line_31)


def without_exclusions(h):
    return {**h, **{v: 0 for v in [*PERSON_EXCLUSIONS, *UNIT_EXCLUSIONS]}}


def exclusions(h):
    return sum(h[v] for v in [*PERSON_EXCLUSIONS, *UNIT_EXCLUSIONS])


def assert_properties(households):
    """Invariants 2 and 3 on a list of households. Returns each household's
    change in the student loan interest deduction from its exclusions."""
    twins = [without_exclusions(h) for h in households]
    model = calculate(households + twins)
    n = len(households)
    changes = []
    for i, h in enumerate(households):
        tol = tolerance(h)
        line_30 = sum(float(values[i]) for values in model["adjustments"].values())
        # 2. Differential against the form.
        assert model["mi_household_resources"][i] == pytest.approx(
            reference(h, line_30), abs=tol
        ), h
        # 3. The exclusions move household resources only through the
        # student loan interest deduction.
        change = (
            model["student_loan_interest_ald"][i]
            - model["student_loan_interest_ald"][n + i]
        )
        assert model["adjusted_gross_income"][n + i] - model["adjusted_gross_income"][
            i
        ] == pytest.approx(exclusions(h) + change, abs=tol), h
        changes.append(float(change))
        without = model["mi_household_resources"][n + i]
        # Resources without exclusions of 0 hide how far below zero they
        # were; a larger deduction (change >= 0) keeps them at 0.
        if without > 0 or change >= 0:
            assert model["mi_household_resources"][i] == pytest.approx(
                max(0, without - change), abs=tol
            ), h
    return changes


def household(**amounts):
    h = {v: 0 for v in [*PERSON_INPUTS, *UNIT_EXCLUSIONS]}
    h.update(amounts)
    return h


# Each exclusion is a share of the income source that holds it.
EXCLUSION_PATTERNS = [
    {},
    {"us_bonds_for_higher_ed": 1_500},
    {"qualified_adoption_assistance_expense": 5_000},
    {"puerto_rico_income": 10_000},
    {"specified_possession_income": 8_000},
    {
        "us_bonds_for_higher_ed": 1_500,
        "qualified_adoption_assistance_expense": 5_000,
        "puerto_rico_income": 10_000,
        "specified_possession_income": 8_000,
    },
]


PATTERN_NAMES = [
    "none",
    "us_bonds_for_higher_ed",
    "qualified_adoption_assistance_expense",
    "puerto_rico_income",
    "specified_possession_income",
    "all",
]


def grid_households():
    """Wages, interest, Schedule C income, exclusions, Schedule 1
    adjustments and premiums in every combination (1,536 households), plus
    each exclusion pattern in the student loan interest phase-out (6)."""
    households = []
    for (
        wages,
        interest,
        exempt,
        schedule_c,
        pattern,
        ewp,
        ira,
        sli,
        premiums,
    ) in itertools.product(
        [0, 40_000],
        [0, 3_000],
        [0, 800],
        [0, 20_000],
        EXCLUSION_PATTERNS,
        [0, 400],
        [0, 2_500],
        [0, 1_500],
        [0, 3_000],
    ):
        h = household(
            employment_income_before_lsr=wages,
            taxable_interest_income=interest,
            tax_exempt_interest_income=exempt,
            self_employment_income=schedule_c,
            early_withdrawal_penalty=ewp,
            traditional_ira_contributions=ira,
            student_loan_interest=sli,
            health_insurance_premiums=premiums,
        )
        # Savings bond interest needs interest; the rest are wages.
        for name, amount in pattern.items():
            source = interest if name == "us_bonds_for_higher_ed" else wages
            h[name] = amount if source >= amount else 0
        households.append(h)
    # In the student loan interest phase-out ($85,000 to $100,000 of modified
    # AGI for a single filer in 2025), where an exclusion changes that
    # deduction.
    for pattern in EXCLUSION_PATTERNS:
        h = household(
            employment_income_before_lsr=92_000,
            taxable_interest_income=3_000,
            student_loan_interest=2_500,
        )
        h.update(pattern)
        households.append(h)
    return households


def test_federal_deductions_are_classified():
    """Invariant 1, for every year from 2021 (when the Michigan list starts)
    and every date the federal list changes after that."""
    parameters = system.parameters
    federal_node = parameters.gov.irs.ald.deductions
    michigan_node = parameters.gov.states.mi.tax.income.household_resources_adjustments
    dates = {f"{year}-01-01" for year in range(2021, 2036)}
    dates |= {
        entry.instant_str
        for node in [federal_node, michigan_node]
        for entry in node.values_list
        if entry.instant_str >= "2021-01-01"
    }
    for date in sorted(dates):
        federal = set(federal_node(date))
        michigan = set(michigan_node(date))
        assert michigan == set(SCHEDULE_1_ADJUSTMENTS), date
        assert not michigan & NOT_SCHEDULE_1_ADJUSTMENTS, date
        assert michigan <= federal, (date, michigan - federal)
        unclassified = federal - michigan - NOT_SCHEDULE_1_ADJUSTMENTS
        assert not unclassified, (
            f"{date}: classify {sorted(unclassified)} for MI-1040CR line 30: add "
            "it to gov.states.mi.tax.income.household_resources_adjustments "
            "and SCHEDULE_1_ADJUSTMENTS here if it is a U.S. Schedule 1 Part "
            "II adjustment, otherwise to NOT_SCHEDULE_1_ADJUSTMENTS."
        )


def test_grid():
    """Invariants 2 and 3 on every grid household. In the phase-out, savings
    bond interest and adoption benefits lower the student loan interest
    deduction's modified AGI, so they change that deduction; Puerto Rico
    income is added back (IRC 221(b)(2)(C)), so it does not. Possession
    income is not checked here: its effect depends on the federal modified
    AGI's treatment of section 931, which is outside this test."""
    changes = assert_properties(grid_households())
    phase_out = dict(zip(PATTERN_NAMES, changes[-len(EXCLUSION_PATTERNS) :]))
    assert phase_out["none"] == 0
    assert phase_out["puerto_rico_income"] == pytest.approx(0, abs=TOLERANCE)
    for name in ["us_bonds_for_higher_ed", "qualified_adoption_assistance_expense"]:
        assert phase_out[name] > 1, name
    assert phase_out["all"] > 1


def test_line_30_follows_the_federal_list():
    """Invariant 4. Removing the early withdrawal penalty and the IRA
    deduction from the federal list takes them off line 30. Removing two
    exclusions as well changes AGI, and household resources still match the
    form: the exclusions were never on line 30, and only the student loan
    interest deduction, read from the model, follows the higher modified
    AGI."""
    households = grid_households()
    removed = {
        "early_withdrawal_penalty",
        "traditional_ira_contributions",
        "us_bonds_for_higher_ed",
        "puerto_rico_income",
    }
    model = calculate(households, reform=without_federal_deductions(removed))
    assert "early_withdrawal_penalty" not in model["adjustments"]
    assert "traditional_ira_contributions" not in model["adjustments"]
    for i, h in enumerate(households):
        line_30 = sum(float(values[i]) for values in model["adjustments"].values())
        assert model["mi_household_resources"][i] == pytest.approx(
            reference(h, line_30), abs=tolerance(h)
        ), h


if hypothesis is not None:
    WAGES = st.integers(min_value=0, max_value=300_000)
    SMALL = st.integers(min_value=0, max_value=20_000)
    # Each example builds a Simulation; on a loaded runner input generation
    # can trip the too_slow health check, which says nothing about the model.
    SLOW = [hypothesis.HealthCheck.too_slow]

    @st.composite
    def drawn_household(draw):
        h = household(
            employment_income_before_lsr=draw(WAGES),
            taxable_interest_income=draw(st.one_of(st.just(0), SMALL)),
            tax_exempt_interest_income=draw(st.one_of(st.just(0), SMALL)),
            self_employment_income=draw(
                st.one_of(st.just(0), st.integers(-50_000, 200_000))
            ),
            early_withdrawal_penalty=draw(st.one_of(st.just(0), SMALL)),
            traditional_ira_contributions=draw(
                st.one_of(st.just(0), st.integers(0, 7_000))
            ),
            student_loan_interest=draw(st.one_of(st.just(0), st.integers(0, 5_000))),
            health_insurance_premiums=draw(st.one_of(st.just(0), SMALL)),
        )
        # Exclusions are drawn as shares of the income that holds them, and
        # the wage-based ones together do not exceed wages.
        h["us_bonds_for_higher_ed"] = draw(st.integers(0, h["taxable_interest_income"]))
        remaining = h["employment_income_before_lsr"]
        for name in [
            "qualified_adoption_assistance_expense",
            "puerto_rico_income",
            "specified_possession_income",
        ]:
            h[name] = draw(st.one_of(st.just(0), st.integers(0, remaining)))
            remaining -= h[name]
        return h

    @hypothesis.settings(max_examples=25, deadline=None, suppress_health_check=SLOW)
    @hypothesis.given(st.lists(drawn_household(), min_size=1, max_size=40))
    def test_properties(households):
        """Invariants 2 and 3 on drawn households."""
        assert_properties(households)
