"""Property tests for the taxation of Railroad Retirement Act benefits.

Invariants, for every input the strategies draw:

I1. IRC 86(d)(1): moving any part of a filer's benefits from title II to the
    tier 1 social security equivalent benefit leaves federal AGI, federal
    income tax, the section 86 taxable amount and Medicaid MAGI unchanged.
I2. IRC 72(r)(1): moving any amount from the taxable part of a private
    pension to the taxable part of the rest of the railroad annuity leaves
    federal AGI and federal income tax unchanged.
I3. 45 U.S.C. 231m(a): a household whose only income is railroad benefits
    owes no state income tax in any state. Idaho's $10 permanent building
    fund tax falls on every required filer, so there the test checks that
    taxable income is zero.
I4. For a wage earner under 65, adding railroad benefits leaves the state's
    AGI unchanged, and in states whose reported AGI includes them it leaves
    state taxable income unchanged. Colorado and South Carolina start from
    federal taxable income, which floors at zero; while the standard
    deduction absorbs some of the benefits, their subtraction exceeds what
    federal taxable income gained, so there the base can only fall.
    STATE_BASE_EXCEPTIONS lists the states with a provision measured with
    federal AGI or federal income tax, which railroad benefits raise.
I5. Totals: railroad_benefits is the sum of its three parts; the title II
    and tier 1 shares sum to the section 86 taxable amount; and
    taxable_railroad_benefits is what the head's and spouse's federal AGI
    includes from the Act, and zero for dependents.
D1. Differential: section 86 runs once on the head and spouse's return and
    once on a dependent's own return. For the same income and benefits the
    two give the same taxable amount.

YAML tests pin worked examples; these properties quantify over amounts,
filing status and every state, which YAML cannot. Each example builds one
Simulation that holds every household it compares.

The model keeps money in float32, whose step grows with the amount: 2^-7
from $65,536 to $131,072 and 2^-6 from there to $262,144. Two calculations
that add the same dollars in a different order can land a few steps apart,
so the comparisons allow eight steps at the largest amount involved, and
never less than a cent.
"""

import numpy as np
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


@settings(max_examples=25, deadline=None)
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
    tol = tolerance(wages + head_benefits + spouse_benefits)
    for variable in (
        "adjusted_gross_income",
        "income_tax",
        "tax_unit_taxable_section_86_benefits",
        "medicaid_magi",
    ):
        title_ii, railroad = calc(simulation, variable)[:2]
        assert abs(title_ii - railroad) < tol, (variable, title_ii, railroad)
    np.testing.assert_allclose(
        section_86_parts(simulation),
        calc(simulation, "tax_unit_taxable_section_86_benefits"),
        atol=tol,
    )


@settings(max_examples=25, deadline=None)
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


@settings(max_examples=6, deadline=None)
@given(
    tier_1=st.integers(min_value=0, max_value=60_000),
    tier_2=st.integers(min_value=1, max_value=80_000),
    tax_free=st.integers(min_value=0, max_value=5_000),
    age=st.integers(min_value=18, max_value=90),
    joint=st.booleans(),
)
def test_i3_no_state_taxes_railroad_benefits(tier_1, tier_2, tax_free, age, joint):
    head = {
        "age": age,
        "railroad_social_security_equivalent_benefits": tier_1,
        "taxable_railroad_pension_benefits": tier_2,
        "tax_exempt_railroad_pension_benefits": tax_free,
    }
    members = [head] + ([head | {"role": "spouse"}] if joint else [])
    simulation = Simulation(
        situation=situation([(state, members) for state in INCOME_TAX_STATES])
    )
    # Tier 2 benefits are always taxable federally, so the test is not vacuous.
    assert calc(simulation, "adjusted_gross_income").min() >= tier_2
    tax = calc(simulation, "state_income_tax_before_refundable_credits")
    idaho_taxable_income = calc(simulation, "id_taxable_income")
    for i, state in enumerate(INCOME_TAX_STATES):
        if state == "ID":
            assert idaho_taxable_income[i] == 0, (state, idaho_taxable_income[i])
        else:
            assert abs(tax[i]) < CENT, (state, tax[i])


@settings(max_examples=6, deadline=None)
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


@settings(max_examples=25, deadline=None)
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
    np.testing.assert_allclose(
        taxable_tier_1.sum(),
        calc(
            simulation, "tax_unit_taxable_railroad_social_security_equivalent_benefits"
        )[0],
        atol=tol,
    )
    np.testing.assert_allclose(
        calc(simulation, "taxable_railroad_benefits"),
        taxable_tier_1 + np.array(tier_2, dtype=float) * [1, 1, 0],
        atol=tol,
    )


@settings(max_examples=25, deadline=None)
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
