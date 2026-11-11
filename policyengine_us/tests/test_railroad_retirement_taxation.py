"""Property tests for the taxation of Railroad Retirement Act benefits.

Invariants, for every input the strategies draw:

I1. IRC 86(d)(1): moving any part of a filer's benefits from title II to the
    tier 1 social security equivalent benefit leaves federal AGI, federal
    income tax, the section 86 taxable amount, Medicaid MAGI and the section
    22 amount unchanged. Section 22(c)(3)(A)(i) reduces that amount by
    nontaxable title II benefits under (I) and by nontaxable Railroad
    Retirement Act benefits under (II).
I2. IRC 72(r)(1): moving any amount from the taxable part of a private
    pension to the taxable part of the rest of the railroad annuity leaves
    federal AGI and federal income tax unchanged.
I3. 45 U.S.C. 231m(a): a household whose only income is railroad benefits
    owes no state income tax in any state in 2025 or 2026, alternative and
    minimum taxes included, and no state's withholding estimate counts the
    benefits.
    Idaho's $10 permanent building fund tax falls on every required filer,
    so there the test checks that taxable income is zero.
I4. For a wage earner under 65 in 2025, with wages up to $120,000 and
    benefits up to $70,000, adding railroad benefits leaves the state's AGI
    unchanged, and in states whose reported AGI includes them it leaves state
    taxable income unchanged. Colorado and South Carolina start from federal
    taxable income, which floors at zero; while the standard deduction
    absorbs some of the benefits, their subtraction exceeds what federal
    taxable income gained, so there the base can only fall.
    STATE_BASE_EXCEPTIONS lists the states with a provision measured with
    federal AGI or federal income tax that binds in that range. Outside it,
    more such provisions bind: Minnesota reduces its standard deduction with
    federal AGI above $238,950 in 2025 and phases out its dependent
    exemptions with federal AGI, and from 2026 South Carolina phases out its
    income adjusted deduction (SCIAD) with federal AGI.
I5. Totals: when railroad_benefits itself is left unset, it is the sum of
    its three parts; the title II and tier 1 shares sum to the section 86
    taxable amount; each spouse carries the share of the unit's taxable tier
    1 amount that their own tier 1 benefits make up; and
    taxable_railroad_benefits is what the head's and spouse's federal AGI
    includes from the Act, and zero for dependents.
I6. Taxpayer Relief Act section 1303, "Income" (2): each dollar of railroad
    benefits a filer or spouse receives, split among the three parts in any
    way or entered as a total, raises Pennsylvania Property Tax/Rent Rebate
    income by 50 cents, whatever share of it federal AGI holds.
D1. Differential: section 86 runs once on the head and spouse's return and
    once on a dependent's own return. For the same income and benefits the
    two give the same taxable amount.

YAML tests pin worked examples; these properties quantify over amounts,
filing status and every state, which YAML cannot. Each example builds one
Simulation that holds every household it compares.

The model keeps money in float32, whose step grows with the amount: 2^-7
from $65,536 to $131,072 and 2^-6 from there to $262,144. Two calculations
that add the same dollars in a different order can land a few steps apart,
so the comparisons allow eight steps at the sum of the income inputs, and
never less than a cent.
"""

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2025
CENT = 0.01


def tolerance(*amounts):
    """Eight float32 steps at the largest of the amounts, or a cent."""
    largest = max(abs(float(amount)) for amount in amounts)
    return max(CENT, 8 * float(np.spacing(np.float32(largest))))


INCOME_TAX_STATES = (
    "AL AZ AR CA CO CT DE DC GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO "
    "MT NE NJ NM NY NC ND OH OK OR PA RI SC UT VT VA WV WI"
).split()

# States whose AGI as taxsim_state_agi reports it includes railroad benefits:
# the states_using_federal_agi list, which reports federal AGI, and Utah,
# which reports TC-40 line 6 total income (federal AGI plus additions) and
# subtracts the benefits on the way to taxable income. I4 compares their
# taxable income.
FEDERAL_AGI_STATES = {"CO", "MI", "MN", "MT", "NC", "ND", "NM", "SC", "UT"}

# co_taxable_income and, before the SCIAD, sc_taxable_income start from
# taxable_income, which floors at zero, and subtract the benefits federal AGI
# includes. North Dakota starts from AGI less deductions without the floor.
FEDERAL_TAXABLE_INCOME_STATES = {"CO", "SC"}

# Provisions measured with federal AGI or federal income tax. Railroad
# benefits raise both, so these states' bases move by the state's own rule.
STATE_BASE_EXCEPTIONS = {
    # or_agi subtracts the federal income tax subtraction (ORS 316.680(1)(b)).
    "OR": "federal income tax subtraction inside Oregon AGI",
    # nm_low_and_middle_income_exemption phases out with adjusted_gross_income
    # (NMSA 7-2-5.8; 7-2-2 defines adjusted gross income as federal AGI).
    "NM": "low- and middle-income exemption phases out on federal AGI",
}
I4_STATES = [s for s in INCOME_TAX_STATES if s not in STATE_BASE_EXCEPTIONS]

ROLE_FLAGS = ("is_tax_unit_head", "is_tax_unit_spouse", "is_tax_unit_dependent")


def situation(households, year=YEAR):
    """Build a situation from (state, members) pairs.

    Each member is a dict of person inputs plus an optional "role": the first
    member defaults to head and the rest to dependent. The head and spouse
    share a marital unit; each dependent has one of its own.
    """
    people, units, households_out, marital_units = {}, {}, {}, {}
    for i, (state, members) in enumerate(households):
        names, couple = [], []
        for j, inputs in enumerate(members):
            inputs = dict(inputs)
            role = inputs.pop("role", "head" if j == 0 else "dependent")
            name = f"h{i}p{j}"
            names.append(name)
            people[name] = {key: {year: value} for key, value in inputs.items()}
            for flag in ROLE_FLAGS:
                people[name][flag] = {year: flag == f"is_tax_unit_{role}"}
            if role == "dependent":
                marital_units[f"{name}m"] = {"members": [name]}
            else:
                couple.append(name)
        marital_units[f"h{i}m"] = {"members": couple}
        units[f"h{i}"] = names
        households_out[f"h{i}"] = {"members": names, "state_name": {year: state}}

    def group():
        return {key: {"members": list(value)} for key, value in units.items()}

    return {
        "people": people,
        "tax_units": group(),
        "spm_units": group(),
        "families": group(),
        "marital_units": marital_units,
        "households": households_out,
    }


def calc(simulation, variable, year=YEAR):
    return np.asarray(simulation.calculate(variable, year), dtype=float)


def section_86_parts(simulation):
    return calc(simulation, "tax_unit_taxable_social_security") + calc(
        simulation, "tax_unit_taxable_railroad_social_security_equivalent_benefits"
    )


amounts = st.integers(min_value=0, max_value=60_000)
wages = st.integers(min_value=0, max_value=150_000)
shares = st.integers(min_value=0, max_value=100).map(lambda x: x / 100)


@settings(max_examples=25, deadline=None, derandomize=True)
@given(
    wages=wages,
    head_benefits=amounts,
    spouse_benefits=amounts,
    head_share=shares,
    spouse_share=shares,
    joint=st.booleans(),
    age=st.integers(min_value=62, max_value=85),
)
# At $131,072 of wages, float32 rounds the two households' AGI one $0.015625
# step apart: the railroad household adds its title II and SSEB shares to AGI
# separately.
@example(
    wages=131_072,
    head_benefits=1,
    spouse_benefits=0,
    head_share=0.01,
    spouse_share=0.0,
    joint=False,
    age=62,
)
# A 70-year-old with no other income keeps a section 22 amount: $5,000 less
# the $2,000 of nontaxable benefits, whichever kind they are.
@example(
    wages=0,
    head_benefits=2_000,
    spouse_benefits=0,
    head_share=1.0,
    spouse_share=0.0,
    joint=False,
    age=70,
)
def test_i1_tier_1_benefits_are_taxed_as_title_ii_benefits(
    wages, head_benefits, spouse_benefits, head_share, spouse_share, joint, age
):
    def person(benefits, railroad_share, role):
        return {
            "role": role,
            "age": age,
            "social_security_retirement": benefits * (1 - railroad_share),
            "railroad_social_security_equivalent_benefits": benefits * railroad_share,
        }

    def household(head_share, spouse_share):
        members = [person(head_benefits, head_share, "head")]
        members[0]["employment_income"] = wages
        if joint:
            members.append(person(spouse_benefits, spouse_share, "spouse"))
        return ("TX", members)

    simulation = Simulation(
        situation=situation([household(0, 0), household(head_share, spouse_share)])
    )
    tol = tolerance(wages + head_benefits + (spouse_benefits if joint else 0))
    for variable in (
        "adjusted_gross_income",
        "income_tax",
        "tax_unit_taxable_section_86_benefits",
        "medicaid_magi",
        "section_22_income",
    ):
        title_ii, railroad = calc(simulation, variable)[:2]
        assert abs(title_ii - railroad) < tol, (variable, title_ii, railroad)
    np.testing.assert_allclose(
        section_86_parts(simulation),
        calc(simulation, "tax_unit_taxable_section_86_benefits"),
        atol=tol,
    )


@settings(max_examples=25, deadline=None, derandomize=True)
@given(
    wages=wages,
    pension=st.integers(min_value=0, max_value=80_000),
    title_ii=amounts,
    age=st.integers(min_value=60, max_value=85),
)
def test_i2_the_rest_of_the_annuity_is_taxed_as_a_pension(
    wages, pension, title_ii, age
):
    base = {
        "age": age,
        "employment_income": wages,
        "social_security_retirement": title_ii,
    }
    simulation = Simulation(
        situation=situation(
            [
                ("TX", [base | {"taxable_pension_income": pension}]),
                ("TX", [base | {"taxable_railroad_pension_benefits": pension}]),
            ]
        )
    )
    tol = tolerance(wages + pension + title_ii)
    for variable in ("adjusted_gross_income", "income_tax"):
        private, railroad = calc(simulation, variable)
        assert abs(private - railroad) < tol, (variable, private, railroad)


@settings(max_examples=6, deadline=None, derandomize=True)
@given(
    tier_1=st.integers(min_value=0, max_value=60_000),
    tier_2=st.integers(min_value=1, max_value=300_000),
    tax_free=st.integers(min_value=0, max_value=5_000),
    age=st.integers(min_value=18, max_value=90),
    joint=st.booleans(),
    year=st.sampled_from((2025, 2026)),
)
# Minnesota's AMT starts from federal AGI (Schedule M1MT line 1) and Vermont's
# minimum tax takes 3% of federal AGI over $150,000 (32 V.S.A. 5822(a)(6)).
# Both bases must leave the benefits out.
@example(tier_1=0, tier_2=64_255, tax_free=0, age=70, joint=True, year=2025)
@example(tier_1=0, tier_2=79_918, tax_free=0, age=18, joint=False, year=2025)
@example(tier_1=0, tier_2=262_000, tax_free=0, age=70, joint=False, year=2025)
@example(tier_1=0, tier_2=262_000, tax_free=0, age=70, joint=False, year=2026)
def test_i3_no_state_taxes_railroad_benefits(
    tier_1, tier_2, tax_free, age, joint, year
):
    head = {
        "age": age,
        "railroad_social_security_equivalent_benefits": tier_1,
        "taxable_railroad_pension_benefits": tier_2,
        "tax_exempt_railroad_pension_benefits": tax_free,
    }
    members = [head] + ([head | {"role": "spouse"}] if joint else [])
    simulation = Simulation(
        situation=situation(
            [(state, members) for state in INCOME_TAX_STATES], year=year
        )
    )
    # Tier 2 benefits are always taxable federally, so the test is not vacuous.
    assert calc(simulation, "adjusted_gross_income", year).min() >= tier_2
    tax = calc(simulation, "state_income_tax_before_refundable_credits", year)
    idaho_taxable_income = calc(simulation, "id_taxable_income", year)
    withholding = calc(simulation, "state_withheld_income_tax", year)
    for i, state in enumerate(INCOME_TAX_STATES):
        if state == "ID":
            assert idaho_taxable_income[i] == 0, (state, idaho_taxable_income[i])
        else:
            assert abs(tax[i]) < CENT, (state, tax[i])
        assert abs(withholding[i]) < CENT, (state, withholding[i])


@settings(max_examples=6, deadline=None, derandomize=True)
@given(
    wages=st.integers(min_value=0, max_value=120_000),
    tier_1=st.integers(min_value=0, max_value=30_000),
    tier_2=st.integers(min_value=0, max_value=40_000),
    age=st.integers(min_value=25, max_value=64),
)
# South Carolina adds back $750 of the 2025 standard deduction for every
# non-itemizer, so a dollar of benefits the standard deduction absorbs still
# lowers its base from 750 to 749.
@example(wages=0, tier_1=0, tier_2=1, age=25)
@example(wages=40_000, tier_1=12_000, tier_2=15_000, age=50)
def test_i4_railroad_benefits_leave_state_bases_unchanged(wages, tier_1, tier_2, age):
    worker = {"age": age, "employment_income": wages}
    retiree = worker | {
        "railroad_social_security_equivalent_benefits": tier_1,
        "taxable_railroad_pension_benefits": tier_2,
    }
    households = [(state, [worker]) for state in I4_STATES] + [
        (state, [retiree]) for state in I4_STATES
    ]
    simulation = Simulation(situation=situation(households))
    n = len(I4_STATES)
    agi = calc(simulation, "taxsim_state_agi")
    taxable_income = calc(simulation, "taxsim_state_taxable_income")
    federal_taxable_income = calc(simulation, "taxable_income")
    tol = tolerance(wages + tier_1 + tier_2)
    for i, state in enumerate(I4_STATES):
        base = taxable_income if state in FEDERAL_AGI_STATES else agi
        before, after = base[i], base[i + n]
        floored = federal_taxable_income[i] <= 0
        if state in FEDERAL_TAXABLE_INCOME_STATES and floored:
            assert after <= before + tol, (state, before, after)
        else:
            assert abs(before - after) < tol, (state, before, after)


@settings(max_examples=25, deadline=None, derandomize=True)
@given(
    tier_1=st.lists(amounts, min_size=3, max_size=3),
    tier_2=st.lists(amounts, min_size=3, max_size=3),
    tax_free=st.lists(
        st.integers(min_value=0, max_value=5_000), min_size=3, max_size=3
    ),
    title_ii=st.lists(amounts, min_size=3, max_size=3),
    earnings=st.lists(wages, min_size=3, max_size=3),
)
def test_i5_railroad_totals_add_up(tier_1, tier_2, tax_free, title_ii, earnings):
    roles, ages = ("head", "spouse", "dependent"), (70, 68, 17)
    members = [
        {
            "role": roles[i],
            "age": ages[i],
            "employment_income": earnings[i],
            "social_security_retirement": title_ii[i],
            "railroad_social_security_equivalent_benefits": tier_1[i],
            "taxable_railroad_pension_benefits": tier_2[i],
            "tax_exempt_railroad_pension_benefits": tax_free[i],
        }
        for i in range(3)
    ]
    simulation = Simulation(situation=situation([("TX", members)]))
    tol = tolerance(sum(earnings) + sum(title_ii) + sum(tier_1) + sum(tier_2))
    np.testing.assert_allclose(
        calc(simulation, "railroad_benefits"),
        np.add(np.add(tier_1, tier_2), tax_free),
    )
    np.testing.assert_allclose(
        section_86_parts(simulation),
        calc(simulation, "tax_unit_taxable_section_86_benefits"),
        atol=tol,
    )
    taxable_tier_1 = calc(
        simulation, "taxable_railroad_social_security_equivalent_benefits"
    )
    # The head's and spouse's shares add up to the tax unit's tier 1 amount.
    assert taxable_tier_1[2] == 0
    unit_taxable_tier_1 = calc(
        simulation, "tax_unit_taxable_railroad_social_security_equivalent_benefits"
    )[0]
    np.testing.assert_allclose(taxable_tier_1.sum(), unit_taxable_tier_1, atol=tol)
    # Each spouse carries the share of it that their own tier 1 benefits make up.
    couple_tier_1 = tier_1[0] + tier_1[1]
    if couple_tier_1 > 0:
        np.testing.assert_allclose(
            taxable_tier_1[:2],
            unit_taxable_tier_1 * np.array(tier_1[:2], dtype=float) / couple_tier_1,
            atol=tol,
        )
    np.testing.assert_allclose(
        calc(simulation, "taxable_railroad_benefits"),
        taxable_tier_1 + np.array(tier_2, dtype=float) * [1, 1, 0],
        atol=tol,
    )


@settings(max_examples=10, deadline=None, derandomize=True)
@given(
    tier_1=amounts,
    tier_2=amounts,
    tax_free=st.integers(min_value=0, max_value=5_000),
    title_ii=amounts,
    earnings=wages,
    joint=st.booleans(),
)
# YAML Cases 3a and 3b of pa_property_tax_or_rent_rebate_income.
@example(
    tier_1=10_000, tier_2=10_000, tax_free=2_000, title_ii=0, earnings=0, joint=False
)
@example(tier_1=20_000, tier_2=30_000, tax_free=0, title_ii=0, earnings=0, joint=False)
def test_i6_pennsylvania_rebate_income_counts_half_of_railroad_benefits(
    tier_1, tier_2, tax_free, title_ii, earnings, joint
):
    total = tier_1 + tier_2 + tax_free
    # SSI and the state supplement would fall as railroad benefits rise, and
    # the rebate half-counts them too, so both stay at zero.
    head = {"age": 67, "employment_income": earnings, "ssi": 0, "pa_ssp": 0}
    spouse = {"role": "spouse", "age": 67, "ssi": 0, "pa_ssp": 0}
    if joint:
        spouse["social_security_retirement"] = title_ii
    else:
        head["social_security_retirement"] = title_ii

    def household(railroad):
        return ("PA", [head | railroad] + ([spouse] if joint else []))

    def added_income(railroad):
        # A variable that any person enters becomes an input for every person,
        # with 0 for the rest, so a household that enters the three tiers and
        # one that enters the total cannot share a simulation. Each runs beside
        # a household without railroad benefits.
        simulation = Simulation(
            situation=situation([household({}), household(railroad)])
        )
        income = calc(simulation, "pa_property_tax_or_rent_rebate_income")
        return income[1] - income[0]

    tiers = added_income(
        {
            "railroad_social_security_equivalent_benefits": tier_1,
            "taxable_railroad_pension_benefits": tier_2,
            "tax_exempt_railroad_pension_benefits": tax_free,
        }
    )
    entered_total = added_income({"railroad_benefits": total})
    tol = tolerance(earnings + title_ii + total)
    assert abs(tiers - total / 2) < tol, tiers
    assert abs(entered_total - total / 2) < tol, entered_total


@settings(max_examples=25, deadline=None, derandomize=True)
@given(wages=wages, title_ii=amounts, tier_1=amounts)
def test_d1_dependent_and_filer_section_86_agree(wages, title_ii, tier_1):
    income = {
        "employment_income": wages,
        "social_security_survivors": title_ii,
        "railroad_social_security_equivalent_benefits": tier_1,
    }
    simulation = Simulation(
        situation=situation(
            [
                ("TX", [{"age": 40} | income]),
                ("TX", [{"age": 45}, {"age": 17} | income]),
            ]
        )
    )
    filer = calc(simulation, "tax_unit_taxable_section_86_benefits")[0]
    dependent = (
        calc(simulation, "dependent_taxable_social_security")
        + calc(
            simulation, "dependent_taxable_railroad_social_security_equivalent_benefits"
        )
    )[2]
    assert abs(filer - dependent) < tolerance(wages + title_ii + tier_1), (
        filer,
        dependent,
    )


@pytest.mark.parametrize("amount", [-5_000, float("inf")])
def test_negative_or_infinite_tier_1_benefits_raise(amount):
    """Box 5 of Form RRB-1099 can be negative when repayments exceed the
    year's benefits. The model doesn't net such amounts as IRS Publication 915
    does, so it rejects them, as it rejects negative title II benefits. It
    also rejects an infinite amount. policyengine-core refuses a NaN input
    before any formula runs, so that case needs no test here."""
    simulation = Simulation(
        situation=situation(
            [
                (
                    "TX",
                    [
                        {
                            "age": 70,
                            "employment_income": 20_000,
                            "social_security_retirement": 20_000,
                            "railroad_social_security_equivalent_benefits": amount,
                        }
                    ],
                )
            ]
        )
    )
    with pytest.raises(ValueError, match="finite and nonnegative"):
        simulation.calculate("adjusted_gross_income", YEAR)
