"""Invariants for the federal exclusions in North Dakota's renter's refund income.

N.D.C.C. 57-02-08.1(5)(c) (https://ndlegis.gov/cencode/t57c02.pdf#page=16)
counts income "from all sources", but excludes "any amount excluded from
income by federal or state law with the exception of income from social
security benefits". nd_renters_refund_income starts from market_income. That
counts wages before payroll deductions, and the tax-exempt parts of interest,
pensions, retirement distributions, disability benefits and alimony, so the
variable subtracts nd_renters_refund_federally_excluded_income. The federal
model also deducts four exclusions above the line, so market_income holds that
income too, and the variable subtracts them as well (excluded_deductions).

Four invariants hold for every input.

1. Every market_income component has a stated treatment. Either federal gross
   income counts it in full, or North Dakota subtracts the part federal law
   excludes, or federal gross income leaves it out although federal law does
   not exclude it (each named below, with the reason). Every above-the-line
   deduction in the federal model is likewise either a deduction, which leaves
   the income in, or an exclusion, which North Dakota subtracts. A new
   component or deduction fails until someone classifies it, so a wider
   market_income cannot bring excluded income into the refund again, as
   #10663's wider market_income did.
2. Each excluded part lies between zero and the market_income component it
   comes from, so the exclusions never exceed what those components hold.
   Each exclusion the model deducts above the line comes out of the tax unit's
   income that holds it: savings bond interest out of the interest North
   Dakota counts, adoption assistance out of wages after payroll deductions,
   and income from Puerto Rico and American Samoa out of market income before
   losses, less the other exclusions. None comes out of social security, so
   with no loss in income and no medical costs, renter's refund income never
   falls below social security, and a dollar of social security raises income
   by a dollar unless income stays at zero.
3. Differential: for a filer whose income comes only from sources that
   market_income and federal gross income share, renter's refund income equals
   irs_gross_income less the exclusions the federal model deducts above the
   line. The statute's federal exclusions and the federal model agree on every
   shared source. For interest, pensions, retirement distributions, disability
   benefits and the deducted exclusions, the two sides read different inputs.
   For wages and alimony both read the same federal variables, so the YAML
   cases and invariant 4 test those against the law.
4. Moving a dollar from the taxable form of a source to its excluded form
   lowers renter's refund income by that dollar, beside a loss elsewhere in
   income, as long as income stays above zero. So does marking a dollar of
   income as one of the exclusions the model deducts above the line. A dollar
   of social security raises it by a dollar, however much of the benefit
   federal law taxes.

YAML pins one household per case. These need random amounts over many
households at once, and lists read from market_income's source file and the
federal parameters.
"""

import re
from pathlib import Path

import numpy as np
import pytest
import yaml
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

PACKAGE = Path(__file__).parent.parent
MARKET_INCOME = PACKAGE / "variables/household/income/person/general/market_income.py"
GROSS_INCOME_SOURCES = PACKAGE / "parameters/gov/irs/gross_income/sources.yaml"
ABOVE_THE_LINE = PACKAGE / "parameters/gov/irs/ald/deductions.yaml"
RENTERS_REFUND = PACKAGE / "parameters/gov/states/nd/tax/property/renters_refund"
ND_DEDUCTED_EXCLUSIONS = RENTERS_REFUND / "excluded_deductions.yaml"
ND_MARKET_INCOME_COMPONENTS = RENTERS_REFUND / "market_income_components.yaml"
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
    "pension_income": ("taxable_pension_income", "IRC 72(b)(1), 402(c)(1)"),
    "retirement_distributions": (
        "taxable_retirement_distributions",
        "IRC 402A(d)(1), 402(c)(1), 403(b)(8), 408(d), 408A(d)(1)",
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


# The federal model's above-the-line deductions. A deduction leaves the income
# it offsets in renter's refund income; the statute excludes only what federal
# law excludes from income.
ABOVE_THE_LINE_DEDUCTIONS = {
    "loss_ald": "IRC 62(a)(3) and 1211(b): capital losses",
    "self_employment_tax_ald": "IRC 164(f)",
    "student_loan_interest_ald": "IRC 221",
    "early_withdrawal_penalty": "IRC 62(a)(9)",
    "alimony_expense_ald": "IRC 215, for the payer under an instrument "
    "executed before 2019",
    "educator_expense_ald": "IRC 62(a)(2)(D)",
    "capped_qualified_tuition_expenses_ald": "IRC 222, before its repeal for "
    "years after 2020",
    "domestic_production_ald": "IRC 199, before its repeal for years after 2017",
    "health_savings_account_ald": "IRC 223(a): contributions outside payroll",
    "self_employed_health_insurance_ald": "IRC 162(l)",
    "self_employed_pension_contribution_ald": "IRC 404",
    "traditional_ira_deduction": "IRC 219",
    "charitable_contributions_ald": "IRC 62(a)(22), which applied to 2020",
}
# Exclusions from gross income that the federal model deducts above the line,
# with market_income holding the income they exclude. North Dakota subtracts
# them.
ABOVE_THE_LINE_EXCLUSIONS = {
    "us_bonds_for_higher_ed": "IRC 135(a)",
    "qualified_adoption_assistance_expense": "IRC 137(a)",
    # IRC 931 reaches only a possession with an implementing agreement in
    # effect (26 CFR 1.931-1(c)(1)); IRS Publication 570 applies it only to
    # American Samoa.
    "specified_possession_income": "IRC 931(a), for American Samoa",
    "puerto_rico_income": "IRC 933",
}
# The two a household records on a person; the other two are tax unit inputs.
PERSON_DEDUCTED_EXCLUSIONS = [
    "qualified_adoption_assistance_expense",
    "us_bonds_for_higher_ed",
]
TAX_UNIT_DEDUCTED_EXCLUSIONS = ["specified_possession_income", "puerto_rico_income"]

PAYROLL_DEDUCTIONS = (
    "traditional_401k_contributions",
    "traditional_403b_contributions",
    "pre_tax_health_insurance_premiums",
    "health_savings_account_payroll_contributions",
    "dependent_care_employer_benefits",
)
# The inputs that feed each partly excluded component.
SOURCE_INPUTS = {
    "employment_income": ("employment_income", *PAYROLL_DEDUCTIONS),
    "interest_income": (
        "interest_income",
        "taxable_interest_income",
        "tax_exempt_interest_income",
    ),
    "pension_income": (
        "pension_income",
        "taxable_private_pension_income",
        "tax_exempt_private_pension_income",
        "taxable_public_pension_income",
        "tax_exempt_public_pension_income",
    ),
    "retirement_distributions": (
        "retirement_distributions",
        "taxable_ira_distributions",
        "tax_exempt_ira_distributions",
        "taxable_401k_distributions",
        "tax_exempt_401k_distributions",
        "taxable_403b_distributions",
        "tax_exempt_403b_distributions",
        "taxable_sep_distributions",
        "tax_exempt_sep_distributions",
    ),
    "disability_benefits": ("disability_benefits", "tax_exempt_disability_benefits"),
    "alimony_income": ("alimony_income", "divorce_year"),
}
assert set(SOURCE_INPUTS) == set(PARTLY_EXCLUDED)


def market_income_components():
    return set(re.findall(r'^\s+"([a-z0-9_]+)",', MARKET_INCOME.read_text(), re.M))


def list_parameter_entries(path):
    """Every name a list parameter has held in any period."""
    raw = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
    return {name for block in raw["values"].values() for name in block}


def gross_income_sources():
    return list_parameter_entries(GROSS_INCOME_SOURCES)


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
    # Income from Puerto Rico and American Samoa comes out of these components
    # before losses, so the list must match market_income's.
    assert list_parameter_entries(ND_MARKET_INCOME_COMPONENTS) == components


def test_each_treatment_matches_the_federal_gross_income_list():
    sources = gross_income_sources()
    counted = set(COUNTED_IN_FULL.values()) | {
        taxable for taxable, _ in PARTLY_EXCLUDED.values()
    }
    assert counted - sources == set()
    # A component that federal gross income starts counting moves to
    # COUNTED_IN_FULL.
    assert not set(COUNTED_THOUGH_GROSS_INCOME_OMITS) & sources


def test_every_above_the_line_deduction_has_a_stated_treatment():
    assert not set(ABOVE_THE_LINE_DEDUCTIONS) & set(ABOVE_THE_LINE_EXCLUSIONS)
    entries = list_parameter_entries(ABOVE_THE_LINE)
    classified = set(ABOVE_THE_LINE_DEDUCTIONS) | set(ABOVE_THE_LINE_EXCLUSIONS)
    assert entries - classified == set(), (
        f"above-the-line deductions with no North Dakota treatment: "
        f"{sorted(entries - classified)}. Say whether each is a deduction, "
        "which leaves its income in renter's refund income, or an exclusion "
        "from gross income, which excluded_deductions subtracts."
    )
    assert classified - entries == set(), "stale entries above"
    assert list_parameter_entries(ND_DEDUCTED_EXCLUSIONS) == set(
        ABOVE_THE_LINE_EXCLUSIONS
    )


def situation(households):
    """Single adults in North Dakota, one per household."""
    people, groups, tax_units = {}, {}, {}
    for index, inputs in enumerate(households):
        name = f"person_{index}"
        people[name] = {
            "age": {YEAR: 40},
            **{
                k: {YEAR: v}
                for k, v in inputs.items()
                if k not in TAX_UNIT_DEDUCTED_EXCLUSIONS
            },
        }
        groups[name] = {"members": [name]}
        tax_units[f"tax_unit_{name}"] = {
            "members": [name],
            **{
                k: {YEAR: v}
                for k, v in inputs.items()
                if k in TAX_UNIT_DEDUCTED_EXCLUSIONS
            },
        }
    return {
        "people": people,
        "tax_units": tax_units,
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


def calculate_by_totals(households, *names):
    """calculate, with one Simulation for each set of totals the households
    report. A total one household reports becomes an input for every person in
    its Simulation, which would hide the parts the others report."""
    groups = {}
    for index, inputs in enumerate(households):
        groups.setdefault(frozenset(set(inputs) & set(TOTALS)), []).append(index)
    results = [np.zeros(len(households)) for _ in names]
    for indices in groups.values():
        values = calculate([households[i] for i in indices], *names)
        for result, value in zip(results, values):
            result[indices] = value
    return results


amount = st.integers(min_value=0, max_value=40_000)


@st.composite
def shared_sources(draw):
    """Nonnegative income from sources market_income and gross income share."""
    deductions = {
        name: draw(st.integers(min_value=0, max_value=8_000))
        for name in PAYROLL_DEDUCTIONS
    }
    disability = draw(amount)
    other_wages = draw(st.integers(min_value=0, max_value=150_000))
    taxable_interest = draw(amount)
    adoption = draw(st.integers(min_value=0, max_value=other_wages))
    possession = draw(st.integers(min_value=0, max_value=other_wages - adoption))
    inputs = {
        # Wages cover the payroll deductions and any adoption assistance.
        "employment_income": sum(deductions.values()) + other_wages,
        **deductions,
        # Exclusions the federal model deducts above the line, each within the
        # income that holds it.
        "qualified_adoption_assistance_expense": adoption,
        "us_bonds_for_higher_ed": draw(
            st.integers(min_value=0, max_value=taxable_interest)
        ),
        "specified_possession_income": possession,
        "puerto_rico_income": draw(
            st.integers(min_value=0, max_value=other_wages - adoption - possession)
        ),
        "taxable_interest_income": taxable_interest,
        "tax_exempt_interest_income": draw(amount),
        "taxable_private_pension_income": draw(amount),
        "tax_exempt_private_pension_income": draw(amount),
        "taxable_public_pension_income": draw(amount),
        "tax_exempt_public_pension_income": draw(amount),
        "taxable_ira_distributions": draw(amount),
        "tax_exempt_ira_distributions": draw(amount),
        "taxable_401k_distributions": draw(amount),
        "tax_exempt_401k_distributions": draw(amount),
        "taxable_403b_distributions": draw(amount),
        "tax_exempt_403b_distributions": draw(amount),
        "taxable_sep_distributions": draw(amount),
        "tax_exempt_sep_distributions": draw(amount),
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
    kept = {k: v for k, v in inputs.items() if k in keep or k == "employment_income"}
    # Taxable interest holds the savings bond interest.
    if "taxable_interest_income" not in kept:
        kept.pop("us_bonds_for_higher_ed", None)
    return kept


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
            "taxable_interest_income": 3_000,
            "us_bonds_for_higher_ed": 2_000,
            "qualified_adoption_assistance_expense": 4_000,
            "puerto_rico_income": 3_000,
        }
    ]
)
def test_renters_refund_income_equals_gross_income_on_shared_sources(households):
    nd_income, gross_income = calculate(
        households, "nd_renters_refund_income", "irs_gross_income"
    )
    deducted = [
        sum(inputs.get(name, 0) for name in ABOVE_THE_LINE_EXCLUSIONS)
        for inputs in households
    ]
    expected = [gross - out for gross, out in zip(gross_income, deducted)]
    assert list(nd_income) == pytest.approx(expected, abs=TOLERANCE)


# Inputs for the bounds test: shared sources, plus totals reported without
# their split, tax-exempt parts larger than the totals they belong to, losses,
# and deducted exclusions larger than the income that should hold them.
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
    inputs["rental_income"] = draw(st.integers(min_value=-60_000, max_value=40_000))
    inputs["strike_benefits"] = draw(amount)
    inputs["social_security_retirement"] = draw(amount)
    for name in draw(
        st.sets(
            st.sampled_from(PERSON_DEDUCTED_EXCLUSIONS + TAX_UNIT_DEDUCTED_EXCLUSIONS)
        )
    ):
        inputs[name] = draw(st.integers(min_value=0, max_value=400_000))
    return inputs


@settings(max_examples=12, deadline=None)
@given(households=st.lists(any_sources(), min_size=1, max_size=6))
def test_each_excluded_part_lies_within_its_component(households):
    # Each household as drawn; then each partly excluded source alone, so a
    # part above its component can't hide behind another part below its own;
    # then each household without its social security.
    alone = [
        {k: v for k, v in inputs.items() if k in SOURCE_INPUTS[component]}
        for inputs in households
        for component in PARTLY_EXCLUDED
    ]
    without_social_security = [
        {k: v for k, v in inputs.items() if k != "social_security_retirement"}
        for inputs in households
    ]
    count = len(households)
    names = [
        "nd_renters_refund_federally_excluded_income",
        "nd_renters_refund_income",
        "social_security",
        *PARTLY_EXCLUDED,
    ]
    excluded, nd_income, social_security, *components = calculate_by_totals(
        households + alone + without_social_security, *names
    )
    assert (excluded >= -TOLERANCE).all()
    assert (nd_income >= 0).all()
    drawn = slice(0, count)
    ceiling = sum(component[drawn].clip(min=0) for component in components)
    assert (excluded[drawn] <= ceiling + TOLERANCE).all()
    for index in range(len(alone)):
        position = count + index
        component = components[index % len(PARTLY_EXCLUDED)][position]
        assert excluded[position] <= max(component, 0) + TOLERANCE
    # Social security counts in full: removing it lowers income by all of it,
    # unless income without it stays at zero.
    with_it = nd_income[drawn]
    without_it = nd_income[-count:]
    benefit = social_security[drawn]
    positive = without_it > TOLERANCE
    assert with_it[positive] - without_it[positive] == pytest.approx(
        benefit[positive], abs=TOLERANCE
    )
    assert (with_it[~positive] <= benefit[~positive] + TOLERANCE).all()
    # With no loss in income, no exclusion comes out of social security.
    no_loss = np.array(
        [min(inputs.values(), default=0) >= 0 for inputs in households], dtype=bool
    )
    assert (with_it[no_loss] >= benefit[no_loss] - TOLERANCE).all()


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
    taxable=st.integers(min_value=1, max_value=60_000),
    exempt=st.integers(min_value=0, max_value=60_000),
    share=st.floats(min_value=0.01, max_value=1),
    wages=st.integers(min_value=0, max_value=100_000),
    social_security=st.integers(min_value=0, max_value=40_000),
    loss_share=st.floats(min_value=0, max_value=1),
)
@example(
    taxable=3_000,
    exempt=0,
    share=2 / 3,
    wages=0,
    social_security=10_000,
    loss_share=0.3,
)
# With wages, so the adoption assistance line moves a dollar too.
@example(
    taxable=3_000,
    exempt=0,
    share=2 / 3,
    wages=1_000,
    social_security=10_000,
    loss_share=0.3,
)
def test_a_dollar_moved_to_its_excluded_form_leaves_income(
    taxable, exempt, share, wages, social_security, loss_share
):
    # Every run moves at least a dollar of every source.
    moved = max(round(taxable * share), 1)
    deferral = round(wages * share)
    # A business loss no larger than social security, so income stays above
    # zero and every dollar shows.
    loss = round(social_security * loss_share)
    households = []
    for taxable_name, exempt_name in SHIFTS:
        base = {
            "employment_income": wages,
            "self_employment_income": -loss,
            "social_security_retirement": social_security,
            taxable_name: taxable,
            exempt_name: exempt,
        }
        shifted = {**base, taxable_name: taxable - moved, exempt_name: exempt + moved}
        # A wage dollar deferred into a traditional 401(k), and a disability
        # dollar from a plan the recipient paid for, leave the same way.
        deferred = {**base, "traditional_401k_contributions": deferral}
        disability = {**base, "disability_benefits": exempt + moved}
        paid_for = {**disability, "tax_exempt_disability_benefits": moved}
        # Social security counts in full however much of it federal law taxes.
        more_social_security = {
            **base,
            "social_security_retirement": social_security + moved,
        }
        # The exclusions the federal model deducts above the line leave the
        # same way: a dollar of taxable interest that IRC 135 excludes, a
        # dollar of wages that IRC 137 excludes as employer adoption
        # assistance, and a dollar of income from Puerto Rico (IRC 933) or
        # American Samoa (IRC 931), which the base's wages and taxable income
        # hold before the loss.
        interest = {**base, "taxable_interest_income": taxable}
        bonds = {**interest, "us_bonds_for_higher_ed": moved}
        adoption = {**base, "qualified_adoption_assistance_expense": min(moved, wages)}
        puerto_rico = {**base, "puerto_rico_income": moved}
        american_samoa = {**base, "specified_possession_income": moved}
        households += [
            base,
            shifted,
            deferred,
            disability,
            paid_for,
            more_social_security,
            interest,
            bonds,
            adoption,
            puerto_rico,
            american_samoa,
        ]
    (income,) = calculate(households, "nd_renters_refund_income")
    size = len(households) // len(SHIFTS)
    for group in range(len(SHIFTS)):
        (
            base,
            shifted,
            deferred,
            disability,
            paid_for,
            more_social_security,
            interest,
            bonds,
            adoption,
            puerto_rico,
            american_samoa,
        ) = income[size * group : size * group + size]
        assert base - shifted == pytest.approx(moved, abs=TOLERANCE)
        assert base - deferred == pytest.approx(deferral, abs=TOLERANCE)
        assert disability - paid_for == pytest.approx(moved, abs=TOLERANCE)
        assert more_social_security - base == pytest.approx(moved, abs=TOLERANCE)
        assert interest - bonds == pytest.approx(moved, abs=TOLERANCE)
        assert base - adoption == pytest.approx(min(moved, wages), abs=TOLERANCE)
        assert base - puerto_rico == pytest.approx(moved, abs=TOLERANCE)
        assert base - american_samoa == pytest.approx(moved, abs=TOLERANCE)


def test_alimony_leaves_income_only_under_a_post_2018_instrument():
    households = [
        {"employment_income": 10_000, "alimony_income": 12_000, "divorce_year": year}
        for year in (2015, 2018, 2019, 2024)
    ]
    (income,) = calculate(households, "nd_renters_refund_income")
    assert list(income) == pytest.approx(
        [22_000, 22_000, 10_000, 10_000], abs=TOLERANCE
    )
