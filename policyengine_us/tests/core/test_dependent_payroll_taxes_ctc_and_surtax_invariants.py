"""Invariants for a tax unit dependent's payroll taxes and contributions.

26 U.S.C. 24(d)(1)(B)(ii) lets a taxpayer with three or more qualifying
children figure the refundable child tax credit from "the taxpayer's social
security taxes" less the EITC, and 24(d)(2)(A) defines those as the taxes on
amounts the taxpayer received and on the taxpayer's self-employment income.
Schedule 8812 line 21 adds the spouse's on a joint return. The Additional
Medicare Tax among them comes from the return's own Form 8959, which counts
the wages of the taxpayer and, on a joint return, the spouse. A dependent's
wages are on the dependent's own Form W-2 and return. The CRFB AGI surtax's
expanded base adds amounts to this return's AGI, so it counts the head's and
spouse's own contributions, exclusions and deductions too.

Each case runs every tax unit twice in one vectorized simulation: once with
the dependents' amounts as drawn and once with them set to zero. For every
tax unit:

1. A dependent's wages, self-employment income, retirement contributions,
   tax-exempt interest, Social Security benefits and health insurance
   premiums never change `ctc_social_security_tax`, the Puerto Rico
   equivalent, `additional_medicare_tax` or the CRFB surtax's additions to
   AGI.
2. A dependent's wages, traditional IRA contributions, 401(k) and 403(b)
   deferrals and Social Security benefits, none of which enters the filer's
   AGI or deductions, never change the filer's AGI, refundable or
   non-refundable CTC, federal income tax or CRFB surtax. A dependent's IRA
   deduction is on the dependent's own return (#9801), so the surtax neither
   subtracts it through AGI nor adds it back.
3. Differential: `ctc_social_security_tax`, the Puerto Rico equivalent,
   `additional_medicare_tax` and the surtax equal an independent numpy
   calculation over the head and spouse.

Invariant 2 leaves out three kinds of dependent amount, which invariant 1
checks with AGI and its taxable Social Security given as inputs:

- A dependent's self-employment income still adds to the filer's qualified
  business income deduction, which sums every member's `qbid_amount`.
- A dependent's tax-exempt interest counts toward the filer's EITC
  investment income limit (#9635).
- Health insurance premiums a parent pays for a dependent may be the
  parent's deductible medical expenses.
"""

from functools import cache

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import CountryTaxBenefitSystem

TOLERANCE = 0.01  # dollars
YEARS = [2019, 2020, 2024, 2026]

# The reform's in_effect parameter also applies its structural reform.
SURTAX_ON = {
    "gov.contrib.crfb.surtax.in_effect": {"2000-01-01.2100-12-31": True},
    "gov.contrib.crfb.surtax.increased_base.in_effect": {"2000-01-01.2100-12-31": True},
}

# Dependent amounts that never enter the filer's AGI, deductions or credits.
OFF_RETURN_INPUTS = [
    "employment_income",
    "traditional_ira_contributions_desired",
    "traditional_401k_contributions_desired",
    "traditional_403b_contributions_desired",
    "social_security_dependents",
]
# Dependent amounts that reach the filer's return elsewhere: see the module
# docstring.
OTHER_INPUTS = [
    "self_employment_income",
    "tax_exempt_interest_income",
    "health_insurance_premiums",
]
PERSON_PAYROLL_TAXES = [
    "employee_social_security_tax",
    "employee_medicare_tax",
    "self_employment_tax_ald_person",
]
PERSON_SURTAX_SOURCES = [
    "traditional_ira_contributions",
    "traditional_401k_contributions",
    "traditional_403b_contributions",
    "student_loan_interest_ald",
    "tax_exempt_interest_income",
    "health_insurance_premiums",
]

money = st.integers(0, 60_000).map(float)


def maybe(strategy):
    """Zero or a draw from the strategy."""
    return st.one_of(st.just(0.0), strategy)


@cache
def surtax_system():
    """The CRFB surtax with its expanded base, built once for every case."""
    return CountryTaxBenefitSystem(reform=SURTAX_ON)


@st.composite
def filer(draw):
    return {
        "age": draw(st.integers(25, 64)),
        "employment_income": draw(maybe(st.integers(1, 300_000).map(float))),
        "self_employment_income": draw(maybe(st.integers(-5_000, 60_000).map(float))),
        # Over the EITC's investment income limit, the alternative refundable
        # CTC formula decides more refunds.
        "taxable_interest_income": draw(maybe(money)),
        "social_security_disability": draw(maybe(money)),
        "traditional_ira_contributions_desired": draw(maybe(st.just(5_000.0))),
        "traditional_401k_contributions_desired": draw(maybe(money)),
        "tax_exempt_interest_income": draw(maybe(money)),
        "health_insurance_premiums": draw(maybe(st.integers(1, 9_000).map(float))),
    }


@st.composite
def dependent(draw, *, every_amount):
    # Under 18, so the model never treats a dependent as a spouse.
    person = {
        "age": draw(st.integers(0, 17)),
        "employment_income": draw(maybe(money)),
        "traditional_ira_contributions_desired": draw(
            maybe(st.integers(1, 7_000).map(float))
        ),
        "traditional_401k_contributions_desired": draw(maybe(money)),
        "traditional_403b_contributions_desired": draw(maybe(money)),
        "social_security_dependents": draw(maybe(st.integers(1, 15_000).map(float))),
    }
    if every_amount:
        person["self_employment_income"] = draw(
            maybe(st.integers(-5_000, 60_000).map(float))
        )
        person["tax_exempt_interest_income"] = draw(maybe(money))
        person["health_insurance_premiums"] = draw(
            maybe(st.integers(1, 9_000).map(float))
        )
    return person


@st.composite
def tax_unit(draw, *, every_amount):
    unit = {
        "head": draw(filer()),
        "spouse": draw(filer()) if draw(st.booleans()) else None,
        "dependents": draw(
            st.lists(dependent(every_amount=every_amount), min_size=1, max_size=5)
        ),
        "excess_payroll_tax_withheld": draw(maybe(st.integers(1, 2_000).map(float))),
    }
    if every_amount:
        unit["adjusted_gross_income"] = draw(st.integers(0, 1_500_000).map(float))
    return unit


def without_dependent_amounts(unit, inputs):
    dependents = [
        {k: (0.0 if k in inputs else v) for k, v in d.items()}
        for d in unit["dependents"]
    ]
    return {**unit, "dependents": dependents}


def build(units, year):
    """A situation with every tax unit, and which people are head or spouse."""
    people, tax_units, marital_units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}
    filer_flags, unit_index = [], []
    for i, unit in enumerate(units):
        members = []
        filers = [("head", unit["head"])]
        if unit["spouse"] is not None:
            filers.append(("spouse", unit["spouse"]))
        roles = filers + [
            (f"dependent{j}", d) for j, d in enumerate(unit["dependents"])
        ]
        for role, values in roles:
            name = f"{role}_{i}"
            people[name] = {k: {year: v} for k, v in values.items()}
            members.append(name)
            filer_flags.append(not role.startswith("dependent"))
            unit_index.append(i)
            if role.startswith("dependent"):
                marital_units[f"marital_unit_{name}"] = {"members": [name]}
        marital_units[f"marital_unit_{i}"] = {"members": members[: len(filers)]}
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            "excess_payroll_tax_withheld": {year: unit["excess_payroll_tax_withheld"]},
        }
        if "adjusted_gross_income" in unit:
            # AGI and the Social Security in it are given, so the filer's
            # AGI cannot carry a dependent's deductions into the surtax.
            taxable_social_security = 0.5 * sum(
                values.get("social_security_disability", 0.0) for _, values in filers
            )
            tax_units[f"tax_unit_{i}"].update(
                adjusted_gross_income={year: unit["adjusted_gross_income"]},
                tax_unit_taxable_social_security={year: taxable_social_security},
            )
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }
        groups["spm_units"][f"spm_unit_{i}"] = {"members": members}
        groups["families"][f"family_{i}"] = {"members": members}
    situation = {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        **groups,
    }
    return situation, np.array(filer_flags), np.array(unit_index)


def filer_sum(values, filers, unit_index):
    """Sum a person-level array over each tax unit's head and spouse."""
    return np.bincount(
        unit_index, weights=values * filers, minlength=unit_index.max() + 1
    )


def run_twice(units, inputs, year, surtax=False):
    """Calculate each unit with its dependents' amounts and without them."""
    zeroed = [without_dependent_amounts(unit, inputs) for unit in units]
    situation, filers, unit_index = build(units + zeroed, year)
    if surtax:
        simulation = Simulation(situation=situation, tax_benefit_system=surtax_system())
    else:
        simulation = Simulation(situation=situation)
    return simulation, filers, unit_index


def calculate(simulation, variable, year):
    return np.asarray(simulation.calculate(variable, year))


def assert_unchanged(simulation, variables, year, n):
    for variable in variables:
        values = calculate(simulation, variable, year)
        np.testing.assert_allclose(
            values[:n], values[n:], atol=TOLERANCE, err_msg=variable
        )


def assert_payroll_taxes_match_reference(simulation, filers, unit_index, year):
    person = {
        v: calculate(simulation, v, year)
        for v in [
            *PERSON_PAYROLL_TAXES,
            "payroll_tax_gross_wages",
            "taxable_self_employment_income",
        ]
    }
    filing_status = simulation.calculate("filing_status", year).decode_to_str()
    p = simulation.tax_benefit_system.parameters(year).gov.irs.payroll.medicare
    threshold = p.additional.exclusion[np.asarray(filing_status)]
    earnings = filer_sum(
        person["payroll_tax_gross_wages"] + person["taxable_self_employment_income"],
        filers,
        unit_index,
    )
    additional_medicare_tax = p.additional.rate * np.maximum(0, earnings - threshold)
    np.testing.assert_allclose(
        calculate(simulation, "additional_medicare_tax", year),
        additional_medicare_tax,
        atol=TOLERANCE,
    )
    payroll_taxes = (
        sum(filer_sum(person[v], filers, unit_index) for v in PERSON_PAYROLL_TAXES)
        + calculate(simulation, "unreported_payroll_tax", year)
        + additional_medicare_tax
    )
    np.testing.assert_allclose(
        calculate(simulation, "pr_refundable_ctc_social_security_tax", year),
        payroll_taxes,
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        calculate(simulation, "ctc_social_security_tax", year),
        payroll_taxes - calculate(simulation, "excess_payroll_tax_withheld", year),
        atol=TOLERANCE,
    )


def assert_surtax_matches_reference(simulation, filers, unit_index, year):
    sources = sum(
        filer_sum(calculate(simulation, v, year), filers, unit_index)
        for v in PERSON_SURTAX_SOURCES
    )
    social_security = filer_sum(
        calculate(simulation, "social_security", year), filers, unit_index
    )
    base = (
        calculate(simulation, "adjusted_gross_income", year)
        + sources
        + calculate(simulation, "health_savings_account_ald", year)
        + calculate(simulation, "foreign_earned_income_exclusion", year)
        + social_security
        - calculate(simulation, "tax_unit_taxable_social_security", year)
    )
    p = simulation.tax_benefit_system.parameters(year).gov.contrib.crfb.surtax
    filing_status = np.asarray(
        simulation.calculate("filing_status", year).decode_to_str()
    )
    expected = np.where(
        filing_status == "JOINT", p.rate.joint.calc(base), p.rate.single.calc(base)
    )
    np.testing.assert_allclose(
        calculate(simulation, "agi_surtax", year), expected, atol=TOLERANCE
    )


def check_off_return_amounts(units, year):
    """Invariants 2 and 3; returns both simulations."""
    n = len(units)
    baseline, filers, unit_index = run_twice(units, OFF_RETURN_INPUTS, year)
    assert_unchanged(
        baseline,
        [
            "adjusted_gross_income",
            "ctc_social_security_tax",
            "pr_refundable_ctc_social_security_tax",
            "additional_medicare_tax",
            "ctc_phase_in",
            "refundable_ctc",
            "non_refundable_ctc",
            "income_tax",
        ],
        year,
        n,
    )
    assert_payroll_taxes_match_reference(baseline, filers, unit_index, year)
    reformed, filers, unit_index = run_twice(
        units, OFF_RETURN_INPUTS, year, surtax=True
    )
    assert_unchanged(reformed, ["agi_surtax"], year, n)
    assert_surtax_matches_reference(reformed, filers, unit_index, year)
    return baseline, reformed


def check_every_amount_with_agi_given(units, year):
    """Invariants 1 and 3."""
    n = len(units)
    simulation, filers, unit_index = run_twice(
        units, OFF_RETURN_INPUTS + OTHER_INPUTS, year, surtax=True
    )
    assert_unchanged(
        simulation,
        [
            "ctc_social_security_tax",
            "pr_refundable_ctc_social_security_tax",
            "additional_medicare_tax",
            "agi_surtax",
        ],
        year,
        n,
    )
    assert_payroll_taxes_match_reference(simulation, filers, unit_index, year)
    assert_surtax_matches_reference(simulation, filers, unit_index, year)


# Each case runs one or two vectorized simulations of up to 24 tax units.
# derandomize keeps CI runs reproducible.
SETTINGS = settings(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@SETTINGS
@given(
    st.lists(tax_unit(every_amount=False), min_size=1, max_size=12),
    st.sampled_from(YEARS),
)
def test_dependents_off_return_amounts_never_change_filer_ctc_tax_or_surtax(
    units, year
):
    check_off_return_amounts(units, year)


@SETTINGS
@given(
    st.lists(tax_unit(every_amount=True), min_size=1, max_size=12),
    st.sampled_from(YEARS),
)
def test_dependents_amounts_never_change_payroll_taxes_or_surtax_additions(units, year):
    check_every_amount_with_agi_given(units, year)


def low_wage_family(married, dependent_wages):
    """Three qualifying children, the EITC barred by interest income and
    wages low enough that payroll taxes decide the refundable CTC."""
    head = {"age": 40, "employment_income": 1_000.0, "taxable_interest_income": 46e3}
    spouse = {"age": 40, "employment_income": 3_000.0} if married else None
    if not married:
        head["employment_income"] = 4_000.0
    children = [
        {"age": 16, "employment_income": dependent_wages},
        {"age": 10},
        {"age": 8},
    ]
    return {
        "head": head,
        "spouse": spouse,
        "dependents": children,
        "excess_payroll_tax_withheld": 0.0,
    }


# The dependent's wages would push the parents over the joint Additional
# Medicare Tax threshold, their IRA deduction would lower the parents' AGI,
# and their contributions and benefits would add to the surtax base.
HIGH_INCOME_COUPLE = {
    "head": {"age": 50, "employment_income": 150_000.0},
    "spouse": {"age": 48, "employment_income": 90_000.0},
    "dependents": [
        {
            "age": 17,
            "employment_income": 25_000.0,
            "traditional_ira_contributions_desired": 5_000.0,
            "traditional_401k_contributions_desired": 5_000.0,
            "social_security_dependents": 6_000.0,
        }
    ],
    "excess_payroll_tax_withheld": 0.0,
}


def test_fixed_households_where_the_alternative_formula_decides():
    units = [
        low_wage_family(married, wages)
        for married in (False, True)
        for wages in (8_000.0, 30_000.0)
    ] + [HIGH_INCOME_COUPLE]
    for year in YEARS:
        baseline, reformed = check_off_return_amounts(units, year)
        # The alternative formula decides each low-wage family's refund.
        ss_tax = calculate(baseline, "ctc_social_security_tax", year)
        eitc = calculate(baseline, "eitc", year)
        earned = calculate(baseline, "ctc_phase_in_relevant_earnings", year)
        refundable = calculate(baseline, "refundable_ctc", year)
        assert (ss_tax[:4] - eitc[:4] > earned[:4] + 1).all()
        np.testing.assert_allclose(refundable[:4], ss_tax[:4], atol=TOLERANCE)
        # The dependent's wages would have raised the couple's tax.
        assert calculate(baseline, "additional_medicare_tax", year)[4] == 0
        # The surtax applies to the couple.
        assert calculate(reformed, "agi_surtax", year)[4] > 0
