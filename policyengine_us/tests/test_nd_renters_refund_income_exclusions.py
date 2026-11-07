"""Invariants for the federal exclusions in North Dakota's renter's refund income.

N.D.C.C. 57-02-08.1(5)(c) (https://ndlegis.gov/cencode/t57c02.pdf#page=16)
counts income "from all sources", but excludes "any amount excluded from
income by federal or state law with the exception of income from social
security benefits". nd_renters_refund_income starts from market_income. That
counts wages before payroll deductions, and the tax-exempt parts of interest,
pensions, retirement distributions, disability benefits and alimony, so the
variable subtracts nd_renters_refund_federally_excluded_income.

Four invariants hold for every input.

1. Every market_income component has a stated treatment. Either federal gross
   income counts it in full, or North Dakota subtracts the part federal law
   excludes, or federal gross income leaves it out although federal law does
   not exclude it (each named below, with the reason). A new component fails
   until it is classified, so a wider market_income cannot bring excluded
   income into the refund again, as #10663's wider market_income did.
2. Each excluded part lies between zero and the market_income component it
   comes from, so the exclusions never exceed what those components hold.
3. Differential: for a filer whose income comes only from sources that
   market_income and federal gross income share, renter's refund income equals
   irs_gross_income. The statute's federal exclusions and the federal gross
   income model agree on every shared source.
4. Moving a dollar from the taxable form of a source to its excluded form
   lowers renter's refund income by that dollar. A dollar of social security
   raises it by a dollar, however much of the benefit federal law taxes.

YAML pins one household per case. These need random amounts over many
households at once, and a list read from market_income's source file.
"""

import re
from pathlib import Path

import pytest
import yaml
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

PACKAGE = Path(__file__).parent.parent
MARKET_INCOME = PACKAGE / "variables/household/income/person/general/market_income.py"
GROSS_INCOME_SOURCES = PACKAGE / "parameters/gov/irs/gross_income/sources.yaml"
YEAR = 2026
# Amounts are float32 in the model.
TOLERANCE = 0.5

# Components federal gross income counts in full, and the gross income source
# that holds each.
COUNTED_IN_FULL = {
    "self_employment_income": "self_employment_income",
    "sstb_self_employment_income": "sstb_self_employment_income",
    "partnership_s_corp_income": "partnership_s_corp_income",
    "dividend_income": "dividend_income",
    "capital_gains": "capital_gains",
    "non_sch_d_capital_gains": "non_sch_d_capital_gains",
    "other_net_gain_person": "other_net_gain_gross_income",
    "rental_income": "rental_income",
    "farm_rent_income": "farm_rent_income",
    "estate_income": "estate_income",
    "illicit_income": "illicit_income",
    "farm_operations_income": "farm_operations_income",
    "miscellaneous_income": "miscellaneous_income",
    "military_retirement_income": "military_retirement_income",
    "ak_permanent_fund_dividend": "ak_permanent_fund_dividend",
}

# Components with a part federal law excludes: the gross income source that
# holds the rest, and the law that excludes the part.
PARTLY_EXCLUDED = {
    "employment_income": (
        "irs_employment_income",
        "IRC 402(e)(3), 402(g)(1), 403(b)(1), 106, 125 and 129(a): pre-tax "
        "payroll deductions",
    ),
    "interest_income": ("taxable_interest_income", "IRC 103(a)"),
    "pension_income": ("taxable_pension_income", "IRC 72(b)(1), 402(c), 402A(d)"),
    "retirement_distributions": (
        "taxable_retirement_distributions",
        "IRC 408(d), 408A(d)(1)",
    ),
    "disability_benefits": ("taxable_disability_benefits", "IRC 104(a)(3)"),
    "alimony_income": (
        "taxable_alimony_income",
        "Pub. L. 115-97 section 11051: instruments executed after 2018",
    ),
}

# Components that federal gross income leaves out although federal law does
# not exclude them in general. North Dakota counts them.
COUNTED_THOUGH_GROSS_INCOME_OMITS = {
    "strike_benefits": "IRS Publication 525 counts strike benefits as income "
    "unless the facts show the union meant them as gifts",
    "gi_cash_assistance": "a guaranteed income payment is a gift (IRC 102) or "
    "public assistance, which the statute counts, depending on the payer, and "
    "the input records neither",
}


def market_income_components():
    return set(re.findall(r'^\s+"([a-z0-9_]+)",', MARKET_INCOME.read_text(), re.M))


def gross_income_sources():
    raw = yaml.load(GROSS_INCOME_SOURCES.read_text(), Loader=yaml.BaseLoader)
    return {name for block in raw["values"].values() for name in block}


def test_every_market_income_component_has_a_stated_treatment():
    lists = (
        set(COUNTED_IN_FULL),
        set(PARTLY_EXCLUDED),
        set(COUNTED_THOUGH_GROSS_INCOME_OMITS),
    )
    for index, first in enumerate(lists):
        for second in lists[index + 1 :]:
            assert not first & second, first & second
    classified = set().union(*lists)
    components = market_income_components()
    assert components - classified == set(), (
        f"market_income components with no North Dakota treatment: "
        f"{sorted(components - classified)}. Say whether federal gross income "
        "counts each in full, or subtract the part federal law excludes in "
        "nd_renters_refund_federally_excluded_income."
    )
    assert classified - components == set(), "stale entries above"


def test_each_treatment_matches_the_federal_gross_income_list():
    sources = gross_income_sources()
    counted = set(COUNTED_IN_FULL.values()) | {
        taxable for taxable, _ in PARTLY_EXCLUDED.values()
    }
    assert counted - sources == set()
    # A component that federal gross income starts counting moves to
    # COUNTED_IN_FULL.
    assert not set(COUNTED_THOUGH_GROSS_INCOME_OMITS) & sources


def situation(households):
    """Single adults in North Dakota, one per household."""
    people, groups = {}, {}
    for index, inputs in enumerate(households):
        name = f"person_{index}"
        people[name] = {"age": {YEAR: 40}, **{k: {YEAR: v} for k, v in inputs.items()}}
        groups[name] = {"members": [name]}
    return {
        "people": people,
        "tax_units": {f"tax_unit_{k}": v for k, v in groups.items()},
        "spm_units": {f"spm_unit_{k}": v for k, v in groups.items()},
        "families": {f"family_{k}": v for k, v in groups.items()},
        "marital_units": {f"marital_unit_{k}": v for k, v in groups.items()},
        "households": {
            f"household_{k}": {**v, "state_code": {YEAR: "ND"}}
            for k, v in groups.items()
        },
    }


def calculate(households, *names):
    simulation = Simulation(situation=situation(households))
    return [simulation.calculate(name, YEAR).astype(float) for name in names]


amount = st.integers(min_value=0, max_value=40_000)


@st.composite
def shared_sources(draw):
    """Nonnegative income from sources market_income and gross income share."""
    deductions = {
        name: draw(st.integers(min_value=0, max_value=8_000))
        for name in (
            "traditional_401k_contributions",
            "traditional_403b_contributions",
            "pre_tax_health_insurance_premiums",
            "health_savings_account_payroll_contributions",
            "dependent_care_employer_benefits",
        )
    }
    disability = draw(amount)
    inputs = {
        # Wages cover the payroll deductions.
        "employment_income": sum(deductions.values())
        + draw(st.integers(min_value=0, max_value=150_000)),
        **deductions,
        "taxable_interest_income": draw(amount),
        "tax_exempt_interest_income": draw(amount),
        "taxable_private_pension_income": draw(amount),
        "tax_exempt_private_pension_income": draw(amount),
        "taxable_public_pension_income": draw(amount),
        "tax_exempt_public_pension_income": draw(amount),
        "taxable_ira_distributions": draw(amount),
        "tax_exempt_ira_distributions": draw(amount),
        "taxable_401k_distributions": draw(amount),
        "tax_exempt_401k_distributions": draw(amount),
        "disability_benefits": disability,
        "tax_exempt_disability_benefits": draw(
            st.integers(min_value=0, max_value=disability)
        ),
        "alimony_income": draw(amount),
        "divorce_year": draw(st.sampled_from([2010, 2018, 2019, 2024])),
        "self_employment_income": draw(amount),
        "qualified_dividend_income": draw(amount),
        "non_qualified_dividend_income": draw(amount),
        "long_term_capital_gains": draw(amount),
        "rental_income": draw(amount),
        "miscellaneous_income": draw(amount),
        "military_retirement_pay": draw(amount),
    }
    # Leave out a random subset, so zero amounts and missing inputs both occur.
    keep = draw(st.sets(st.sampled_from(sorted(inputs))))
    return {k: v for k, v in inputs.items() if k in keep or k == "employment_income"}


@settings(max_examples=12, deadline=None)
@given(households=st.lists(shared_sources(), min_size=1, max_size=12))
@example(
    households=[
        {
            "employment_income": 50_000,
            "traditional_401k_contributions": 5_000,
            "tax_exempt_interest_income": 5_000,
            "tax_exempt_private_pension_income": 4_000,
            "alimony_income": 12_000,
            "divorce_year": 2020,
        }
    ]
)
def test_renters_refund_income_equals_gross_income_on_shared_sources(households):
    nd_income, gross_income = calculate(
        households, "nd_renters_refund_income", "irs_gross_income"
    )
    assert list(nd_income) == pytest.approx(list(gross_income), abs=TOLERANCE)


# Inputs for the bounds test: shared sources, plus totals reported without
# their split and tax-exempt parts larger than the totals they belong to.
TOTALS = ("interest_income", "pension_income", "retirement_distributions")


@st.composite
def any_sources(draw):
    inputs = draw(shared_sources())
    for name in draw(st.sets(st.sampled_from(TOTALS))):
        inputs[name] = draw(amount)
    if draw(st.booleans()):
        inputs["tax_exempt_disability_benefits"] = inputs.get(
            "disability_benefits", 0
        ) + draw(amount)
    inputs["capital_gains"] = draw(st.integers(min_value=-60_000, max_value=40_000))
    inputs["strike_benefits"] = draw(amount)
    return inputs


@settings(max_examples=12, deadline=None)
@given(households=st.lists(any_sources(), min_size=1, max_size=12))
def test_each_excluded_part_lies_within_its_component(households):
    names = ["nd_renters_refund_federally_excluded_income", "nd_renters_refund_income"]
    names += list(PARTLY_EXCLUDED)
    excluded, nd_income, *components = calculate(households, *names)
    ceiling = sum(component.clip(min=0) for component in components)
    assert (excluded >= -TOLERANCE).all()
    assert (excluded <= ceiling + TOLERANCE).all()
    assert (nd_income >= 0).all()


# Each pair moves a dollar from the taxable form of a source to its excluded
# form.
SHIFTS = [
    ("taxable_interest_income", "tax_exempt_interest_income"),
    ("taxable_private_pension_income", "tax_exempt_private_pension_income"),
    ("taxable_public_pension_income", "tax_exempt_public_pension_income"),
    ("taxable_ira_distributions", "tax_exempt_ira_distributions"),
    ("taxable_401k_distributions", "tax_exempt_401k_distributions"),
    ("taxable_403b_distributions", "tax_exempt_403b_distributions"),
    ("taxable_sep_distributions", "tax_exempt_sep_distributions"),
]


@settings(max_examples=12, deadline=None)
@given(
    shift=st.sampled_from(SHIFTS),
    taxable=st.integers(min_value=1, max_value=60_000),
    exempt=st.integers(min_value=0, max_value=60_000),
    share=st.floats(min_value=0, max_value=1),
    wages=st.integers(min_value=0, max_value=100_000),
    social_security=st.integers(min_value=0, max_value=40_000),
)
def test_a_dollar_moved_to_its_excluded_form_leaves_income(
    shift, taxable, exempt, share, wages, social_security
):
    taxable_name, exempt_name = shift
    moved = round(taxable * share)
    base = {
        "employment_income": wages,
        "social_security_retirement": social_security,
        taxable_name: taxable,
        exempt_name: exempt,
    }
    shifted = {**base, taxable_name: taxable - moved, exempt_name: exempt + moved}
    # A wage dollar deferred into a traditional 401(k), and a disability
    # dollar from a plan the recipient paid for, leave the same way.
    deferral = round(wages * share)
    deferred = {**base, "traditional_401k_contributions": deferral}
    disability = {**base, "disability_benefits": exempt + moved}
    paid_for = {**disability, "tax_exempt_disability_benefits": moved}
    # Social security counts in full however much of it is taxed.
    more_social_security = {
        **base,
        "social_security_retirement": social_security + moved,
    }
    households = [base, shifted, deferred, disability, paid_for, more_social_security]
    (income,) = calculate(households, "nd_renters_refund_income")
    assert income[0] - income[1] == pytest.approx(moved, abs=TOLERANCE)
    assert income[0] - income[2] == pytest.approx(deferral, abs=TOLERANCE)
    assert income[3] - income[4] == pytest.approx(moved, abs=TOLERANCE)
    assert income[5] - income[0] == pytest.approx(moved, abs=TOLERANCE)


def test_alimony_leaves_income_only_under_a_post_2018_instrument():
    households = [
        {"employment_income": 10_000, "alimony_income": 12_000, "divorce_year": year}
        for year in (2015, 2018, 2019, 2024)
    ]
    (income,) = calculate(households, "nd_renters_refund_income")
    assert list(income) == pytest.approx(
        [22_000, 22_000, 10_000, 10_000], abs=TOLERANCE
    )
