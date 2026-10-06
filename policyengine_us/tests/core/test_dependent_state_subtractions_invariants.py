"""Property tests: a dependent's own items stay off the filers' DC, Delaware
and Ohio returns, and per-return amounts are counted once.

DC, Delaware and Ohio subtract per-person items from each person's federal
adjusted gross income and pool every member into the filer's state AGI
(dc_taxable_income_joint, de_agi_joint, oh_agi). Federal adjusted gross income
leaves out a tax unit dependent's income (irs_gross_income); the dependent
reports it, and takes these subtractions, on their own return. Each subtracted
item is the taxpayer's own:

- DC subtracts income "included in federal gross income" or entered from the
  filer's federal return (D.C. Code 47-1803.02(a)(2)(A), (E), (L), (LL); D-40
  lines 9, 10 and 13), the D-2440 disability income exclusion ((M)), one per
  return with a column for you and one for your spouse, and up to $10,000 of
  a disabled person's own income ((V)).
- Delaware subtracts income "to the extent included in federal adjusted gross
  income" (30 Del. C. 1106(b)(4), (9), (10)) and 529 contributions made by
  the individual, or by the spouses on a joint return ((b)(11)).
- Ohio deducts the taxpayer's own income and expenses (R.C. 5747.01(A)(4),
  (11), (18), (23), (27), (31)), and the medical and 529 amounts the taxpayer
  paid, including for dependents ((A)(9), (A)(10)).

So for every tax unit in these states, and any income items its dependents
have (unemployment compensation, state tax refunds, U.S. government interest,
D-2440 disability payments, SSI, Pell grants, disability benefits, Ohio
section 179 add-backs, uniformed services retirement and educator expenses):

1. DC, Delaware and Ohio AGI, taxable income and tax before credits are the
   same as when the dependents have none of these items.
2. A dependent's dc_income_subtractions and de_subtractions are zero, and
   their oh_deductions are their shares of the filer's 529 and medical
   deductions.
3. Per-return amounts are counted once over the tax unit:
   - the Ohio unreimbursed medical deduction is the members' medical expenses
     over 7.5% of federal AGI;
   - the DC disability exclusion is the filers' capped payments less federal
     AGI over taxable Social Security plus $15,000.

Dependents are 1 to 17, so they are qualifying children with no income test.
Amounts are whole dollars of at most $200,000.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2025
TOLERANCE = 0.01

# A dependent's own items, zeroed in the twin.
OWN_ITEMS = [
    "unemployment_compensation",
    "salt_refund_income",
    "taxable_interest_income",
    "us_govt_interest_person",
    "total_disability_payments",
    "ssi",
    "pell_grant",
    "disability_benefits",
    "oh_section_179_expense_add_back",
    "oh_uniformed_services_retirement_income_deduction",
    "oh_educator_expense_deduction_person",
]
# The filer's amounts, recorded on whoever they were for.
FILER_ITEMS = [
    "other_medical_expenses",
    "investment_in_529_plan_indv",
    "count_529_contribution_beneficiaries",
]
SAME_AS_WITHOUT_DEPENDENT_ITEMS = {
    "DC": [
        "dc_taxable_income_joint",
        "dc_income_tax_before_credits",
    ],
    "DE": [
        "de_income_tax_before_non_refundable_credits_unit",
    ],
    "OH": [
        "oh_agi",
        "oh_taxable_income",
        "oh_income_tax_before_non_refundable_credits",
    ],
}
UNIT_OUTPUTS = sorted(
    {v for variables in SAME_AS_WITHOUT_DEPENDENT_ITEMS.values() for v in variables}
    | {
        "adjusted_gross_income",
        "tax_unit_taxable_social_security",
        "oh_unreimbursed_medical_care_expense_deduction",
    }
)
PERSON_OUTPUTS = [
    "dc_income_subtractions",
    "dc_disability_exclusion",
    "de_subtractions",
    "de_agi_joint",
    "oh_deductions",
    "oh_529_plan_deduction_person",
    "oh_unreimbursed_medical_care_expense_deduction_person",
    "is_tax_unit_dependent",
]


def amount(low, high):
    return st.integers(low, high).map(float)


def maybe(draw, high):
    """Zero half the time, so items also appear alone."""
    return draw(st.one_of(st.just(0.0), amount(0, high)))


@st.composite
def items(draw):
    interest = maybe(draw, 20_000)
    return {
        "unemployment_compensation": maybe(draw, 20_000),
        "salt_refund_income": maybe(draw, 5_000),
        "taxable_interest_income": interest,
        "us_govt_interest_person": draw(amount(0, int(interest))),
        "total_disability_payments": maybe(draw, 8_000),
        "ssi": maybe(draw, 10_000),
        "pell_grant": maybe(draw, 7_000),
        "disability_benefits": maybe(draw, 20_000),
        "oh_section_179_expense_add_back": maybe(draw, 5_000),
        "oh_uniformed_services_retirement_income_deduction": maybe(draw, 30_000),
        "oh_educator_expense_deduction_person": maybe(draw, 300),
        "other_medical_expenses": maybe(draw, 20_000),
        "investment_in_529_plan_indv": maybe(draw, 5_000),
        "count_529_contribution_beneficiaries": draw(st.integers(0, 2)),
    }


@st.composite
def tax_units(draw):
    state = draw(st.sampled_from(["DC", "DE", "OH"]))
    n_filers = draw(st.integers(1, 2))
    filers = [
        {
            "age": draw(st.integers(25, 64)),
            # Low wages too, where the D-2440 exclusion applies.
            "employment_income": draw(amount(0, 200_000)),
            "is_permanently_and_totally_disabled": draw(st.booleans()),
            **draw(items()),
        }
        for _ in range(n_filers)
    ]
    dependents = [
        {
            "age": draw(st.integers(1, 17)),
            "is_permanently_and_totally_disabled": draw(st.booleans()),
            **draw(items()),
        }
        for _ in range(draw(st.integers(1, 3)))
    ]
    return {"state": state, "filers": filers, "dependents": dependents}


def without_dependent_items(unit):
    zero = {name: 0.0 for name in OWN_ITEMS}
    return {**unit, "dependents": [{**d, **zero} for d in unit["dependents"]]}


def build_situation(units):
    """One tax unit per household: the head, an optional spouse and the
    dependents, each dependent in a marital unit of their own."""
    people, tax_units_out, marital_units, households = {}, {}, {}, {}
    for i, unit in enumerate(units):
        members = []
        for j, person in enumerate(unit["filers"] + unit["dependents"]):
            name = f"person_{i}_{j}"
            filer = j < len(unit["filers"])
            people[name] = {
                "is_tax_unit_head": {YEAR: j == 0},
                "is_tax_unit_spouse": {YEAR: j == 1 and filer},
                "is_tax_unit_dependent": {YEAR: not filer},
                **{key: {YEAR: value} for key, value in person.items()},
            }
            members.append(name)
            if not filer:
                marital_units[f"dependent_{i}_{j}"] = {"members": [name]}
        tax_units_out[f"tax_unit_{i}"] = {"members": members}
        marital_units[f"filers_{i}"] = {"members": members[: len(unit["filers"])]}
        households[f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: unit["state"]},
        }
    return {
        "people": people,
        "tax_units": tax_units_out,
        "marital_units": marital_units,
        "households": households,
    }


def calculate(units):
    simulation = Simulation(situation=build_situation(units))
    unit_results = {
        variable: np.asarray(simulation.calculate(variable, YEAR))
        for variable in UNIT_OUTPUTS
    }
    person_results = {
        variable: np.asarray(simulation.calculate(variable, YEAR))
        for variable in PERSON_OUTPUTS
    }
    p = simulation.tax_benefit_system.parameters(YEAR).gov
    return unit_results, person_results, p


def unit_index(units):
    """The tax unit of each person, in the order build_situation adds them."""
    return np.concatenate(
        [
            np.full(len(unit["filers"]) + len(unit["dependents"]), i)
            for i, unit in enumerate(units)
        ]
    )


def unit_sum(values, index, n):
    return np.bincount(index, weights=values, minlength=n)


def person_inputs(units, name):
    return np.array(
        [
            person[name]
            for unit in units
            for person in unit["filers"] + unit["dependents"]
        ]
    )


def check(units):
    twins = [without_dependent_items(unit) for unit in units]
    unit_results, person_results, p = calculate(units + twins)
    n = len(units)
    states = np.array([unit["state"] for unit in units])
    index = unit_index(units)
    n_people = len(index)
    people = {name: values[:n_people] for name, values in person_results.items()}
    person_state = states[index]
    dependent = people["is_tax_unit_dependent"].astype(bool)

    # 1. The same state AGI, taxable income and tax as without the
    # dependents' own items.
    for state, variables in SAME_AS_WITHOUT_DEPENDENT_ITEMS.items():
        in_state = states == state
        for variable in variables:
            np.testing.assert_allclose(
                unit_results[variable][:n][in_state],
                unit_results[variable][n:][in_state],
                atol=TOLERANCE,
                err_msg=variable,
            )
    in_de = person_state == "DE"
    np.testing.assert_allclose(
        unit_sum(people["de_agi_joint"], index, n)[states == "DE"],
        unit_sum(person_results["de_agi_joint"][n_people:], index, n)[states == "DE"],
        atol=TOLERANCE,
        err_msg="de_agi_joint",
    )

    # 2. Dependents' rows.
    in_dc = person_state == "DC"
    in_oh = person_state == "OH"
    assert np.all(people["dc_income_subtractions"][dependent & in_dc] == 0)
    assert np.all(people["de_subtractions"][dependent & in_de] == 0)
    np.testing.assert_allclose(
        people["oh_deductions"][dependent & in_oh],
        (
            people["oh_529_plan_deduction_person"]
            + people["oh_unreimbursed_medical_care_expense_deduction_person"]
        )[dependent & in_oh],
        atol=TOLERANCE,
    )

    # 3. Per-return amounts counted once.
    agi = unit_results["adjusted_gross_income"][:n]
    is_oh = states == "OH"
    medical = unit_sum(person_inputs(units, "other_medical_expenses"), index, n)
    oh_rate = p.states.oh.tax.income.deductions.unreimbursed_medical_care_expenses.rate
    expected_medical = np.maximum(0, medical - oh_rate * agi)
    np.testing.assert_allclose(
        unit_sum(
            people["oh_unreimbursed_medical_care_expense_deduction_person"], index, n
        )[is_oh],
        expected_medical[is_oh],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        unit_results["oh_unreimbursed_medical_care_expense_deduction"][:n][is_oh],
        expected_medical[is_oh],
        atol=TOLERANCE,
    )

    is_dc = states == "DC"
    d2440 = p.irs.income.disability_income_exclusion
    filer = ~dependent
    capped = filer * np.minimum(
        person_inputs(units, "total_disability_payments"), d2440.cap
    )
    reduced = np.maximum(
        0,
        agi - unit_results["tax_unit_taxable_social_security"][:n] - d2440.amount,
    )
    expected_d2440 = np.maximum(0, unit_sum(capped, index, n) - reduced)
    np.testing.assert_allclose(
        unit_sum(people["dc_disability_exclusion"], index, n)[is_dc],
        expected_d2440[is_dc],
        atol=TOLERANCE,
    )
    assert np.all(people["dc_disability_exclusion"][dependent & in_dc] == 0)


# A simulation's cost is mostly fixed, so each example is a batch of tax
# units and there are few examples.
@settings(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(tax_units(), min_size=10, max_size=30))
def test_dependent_items_stay_off_dc_de_and_oh_returns(units):
    check(units)


def test_reported_examples():
    """A head with $60,000 of wages and a dependent child with their own
    unemployment compensation, state tax refund, disability exclusion and
    Ohio items, in each state; and an Ohio household whose medical deduction
    used to be given to every member."""
    zero = {name: 0.0 for name in OWN_ITEMS + FILER_ITEMS}
    filer = {
        "age": 40,
        "employment_income": 60_000.0,
        "is_permanently_and_totally_disabled": False,
        **zero,
    }
    child = {
        "age": 15,
        "is_permanently_and_totally_disabled": True,
        **zero,
        "unemployment_compensation": 10_000.0,
        "salt_refund_income": 5_000.0,
        "ssi": 9_000.0,
        "pell_grant": 3_000.0,
        "disability_benefits": 3_000.0,
        "oh_section_179_expense_add_back": 3_000.0,
    }
    units = [
        {"state": state, "filers": [filer], "dependents": [child]}
        for state in ["DC", "DE", "OH"]
    ]
    units.append(
        {
            "state": "OH",
            "filers": [{**filer, "other_medical_expenses": 6_000.0}],
            "dependents": [{**zero, "age": 10, "other_medical_expenses": 3_000.0}],
        }
    )
    check(units)
    unit_results, person_results, _ = calculate(units)
    # DC: $60,000 less the $22,500 head of household standard deduction.
    assert unit_results["dc_taxable_income_joint"][0] == 37_500
    # Ohio: 9,000 of medical expenses over 7.5% of 60,000, once.
    assert unit_results["oh_unreimbursed_medical_care_expense_deduction"][3] == 4_500
