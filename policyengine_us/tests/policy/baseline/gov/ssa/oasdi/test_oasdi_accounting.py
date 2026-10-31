"""Generated OASDI accounting identities and a differential with existing outputs.

The variable YAML files hold the hand-computed examples. Python quantifies the
accounting identities over generated multi-person households and compares
existing outputs with and without the new variables in the calculation.
Each draw builds households of one to three adults in one or two tax units,
plus fixed boundary witnesses, in one vectorized simulation that shares the
benefit-taxation counterfactuals across the batch.

Invariants, for every generated household:

1. ``oasdi_payroll_tax_revenue`` is the sum of the three worker-level OASDI tax
   leaves, is nonnegative, and never exceeds the combined OASDI rate times the
   capped base ``min(wage base, covered wages + SE net earnings)``.
2. ``oasdi_income`` equals the members' payroll liabilities plus each tax
   unit's ``tob_revenue_oasdi`` and ``s770_revenue_oasdi``, each counted once.
   The reference uses the generated memberships, not the model's mapping.
3. ``oasdi_cost`` equals the members' ``social_security``, and
   ``oasdi_modeled_balance`` equals ``oasdi_income - oasdi_cost``.
4. With no section 8 option enabled, ``oasdi_niit_revenue`` is zero, including
   for units that owe net investment income tax.
5. Differential: calculating the new outputs leaves the existing outputs equal
   to those of a fresh simulation that never calculates them.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

YEAR = 2026
PAYROLL = system.parameters(YEAR).gov.irs.payroll.social_security
SE_RATE = system.parameters(YEAR).gov.irs.self_employment.rate.social_security
CAP = PAYROLL.cap
# The largest OASDI rate on any dollar of covered earnings.
COMBINED_RATE = max(PAYROLL.rate.employee + PAYROLL.rate.employer, SE_RATE)
# Float32 tax arithmetic can lose a few mills at the upper generated bound.
TOLERANCE = 0.01

LEAVES = (
    "employee_social_security_tax",
    "employer_social_security_tax",
    "self_employment_social_security_tax",
)
NEW = (
    "oasdi_payroll_tax_revenue",
    "oasdi_benefit_taxation_revenue",
    "oasdi_niit_revenue",
    "oasdi_income",
    "oasdi_cost",
    "oasdi_modeled_balance",
)
# Existing outputs the new variables read, or that share their branches.
EXISTING = (
    *LEAVES,
    "employer_total_social_security_tax",
    "taxable_earnings_for_social_security",
    "taxable_self_employment_income",
    "payroll_tax_gross_wages",
    "social_security",
    "tax_unit_taxable_social_security",
    "income_tax",
    "net_investment_income_tax",
    "tob_revenue_oasdi",
    "tob_revenue_medicare_hi",
    "s770_revenue_oasdi",
)


def adult(wages=0, se=0, benefits=0, interest=0, age=40):
    return dict(
        employment_income=wages,
        self_employment_income=se,
        social_security_retirement=benefits,
        taxable_interest_income=interest,
        age=age,
    )


# Each household is (members, whether the first two file jointly).
FIXED_HOUSEHOLDS = (
    # Wages exactly at the base, and wages plus SE earnings filling it.
    ([adult(wages=CAP), adult(wages=CAP - 18_470, se=20_000)], False),
    # A self-employment loss pays no SECA.
    ([adult(se=-20_000)], False),
    # A beneficiary couple who owe tax on benefits, with a worker who files
    # separately in the same household.
    (
        [
            adult(benefits=15_000, interest=50_000, age=70),
            adult(benefits=15_000, age=70),
            adult(wages=50_000),
        ],
        True,
    ),
    # The unit owes net investment income tax, but no section 8 option applies.
    ([adult(wages=300_000, interest=100_000)], False),
)

PERSON = st.builds(
    adult,
    wages=st.one_of(st.just(0), st.integers(0, 300_000)),
    se=st.one_of(st.just(0), st.integers(-20_000, 150_000)),
    benefits=st.one_of(st.just(0), st.integers(0, 40_000)),
    interest=st.one_of(st.just(0), st.integers(0, 150_000)),
    age=st.sampled_from([40, 70]),
)
HOUSEHOLD = st.tuples(st.lists(PERSON, min_size=1, max_size=3), st.booleans())


def build(households):
    """Return a situation and each person's and tax unit's household."""
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
    person_household, tax_unit_household = {}, {}
    for h, (members, joint) in enumerate(households):
        names = [f"person_{h}_{i}" for i in range(len(members))]
        for name, inputs in zip(names, members):
            situation["people"][name] = {
                key: {YEAR: value} for key, value in inputs.items()
            }
            person_household[name] = h
        if joint and len(names) >= 2:
            groups = [names[:2], *([name] for name in names[2:])]
        else:
            groups = [[name] for name in names]
        for t, group in enumerate(groups):
            tax_unit = f"tax_unit_{h}_{t}"
            filing_status = "JOINT" if len(group) == 2 else "SINGLE"
            for j, name in enumerate(group):
                situation["people"][name]["tax_unit_role_input"] = {
                    YEAR: "HEAD" if j == 0 else "SPOUSE"
                }
            situation["tax_units"][tax_unit] = {
                "members": group,
                "filing_status": {YEAR: filing_status},
                # Keep optional itemized deductions out of the counterfactuals.
                "itemized_medical_expenses": {YEAR: 0},
                "salt_deduction": {YEAR: 0},
            }
            situation["marital_units"][f"marital_unit_{h}_{t}"] = {"members": group}
            tax_unit_household[tax_unit] = h
        situation["households"][f"household_{h}"] = {
            "members": names,
            "state_code": {YEAR: "TX"},
        }
        # Missing group entities default to one group containing everyone,
        # so define each explicitly to keep households independent.
        for entity in ("spm_units", "families"):
            situation[entity][f"unit_{h}"] = {"members": names}
        situation["spm_units"][f"unit_{h}"]["takes_up_tanf_if_eligible"] = {YEAR: False}
    return situation, person_household, tax_unit_household


def positions(sim, entity, names):
    index = {name: i for i, name in enumerate(sim.populations[entity].ids)}
    return np.array([index[name] for name in names])


@settings(
    max_examples=3,
    derandomize=True,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(HOUSEHOLD, min_size=4, max_size=6))
def test_oasdi_accounting_identities(generated):
    households = (*FIXED_HOUSEHOLDS, *generated)
    situation, person_household, tax_unit_household = build(households)
    sim = Simulation(situation=situation)
    new = {name: np.asarray(sim.calculate(name, YEAR)).copy() for name in NEW}
    existing = {name: np.asarray(sim.calculate(name, YEAR)).copy() for name in EXISTING}

    # 1. Payroll liability: three leaves, nonnegative, within the capped base.
    payroll = new["oasdi_payroll_tax_revenue"]
    np.testing.assert_allclose(
        payroll, sum(existing[leaf] for leaf in LEAVES), rtol=0, atol=TOLERANCE
    )
    covered = (
        existing["payroll_tax_gross_wages"] + existing["taxable_self_employment_income"]
    )
    assert np.all(payroll >= 0)
    assert np.all(payroll <= COMBINED_RATE * np.minimum(CAP, covered) + TOLERANCE)
    # The employer-aggregate liability stays outside the sum.
    assert np.all(existing["employer_total_social_security_tax"] == 0)

    # 2. Household liabilities count each person and tax unit once.
    people = positions(sim, "person", list(person_household))
    tax_units = positions(sim, "tax_unit", list(tax_unit_household))
    n_households = len(households)
    np.testing.assert_array_equal(
        new["oasdi_benefit_taxation_revenue"], existing["tob_revenue_oasdi"]
    )
    np.testing.assert_array_equal(
        new["oasdi_niit_revenue"], existing["s770_revenue_oasdi"]
    )
    tax_unit_revenue = new["oasdi_benefit_taxation_revenue"] + new["oasdi_niit_revenue"]
    reference_income = np.bincount(
        list(person_household.values()),
        weights=payroll[people].astype(float),
        minlength=n_households,
    ) + np.bincount(
        list(tax_unit_household.values()),
        weights=tax_unit_revenue[tax_units].astype(float),
        minlength=n_households,
    )
    household_positions = positions(
        sim, "household", [f"household_{h}" for h in range(n_households)]
    )
    income = new["oasdi_income"][household_positions]
    np.testing.assert_allclose(income, reference_income, rtol=0, atol=TOLERANCE)

    # 3. Modeled benefits and the modeled balance.
    reference_cost = np.bincount(
        list(person_household.values()),
        weights=existing["social_security"][people].astype(float),
        minlength=n_households,
    )
    cost = new["oasdi_cost"][household_positions]
    np.testing.assert_allclose(cost, reference_cost, rtol=0, atol=TOLERANCE)
    np.testing.assert_allclose(
        new["oasdi_modeled_balance"][household_positions],
        income - cost,
        rtol=0,
        atol=TOLERANCE,
    )

    # 4. No section 8 option: no transfer, though some units owe NIIT.
    assert np.all(new["oasdi_niit_revenue"] == 0)
    assert np.any(existing["net_investment_income_tax"] > 0)
    # The fixed witnesses keep the checks above from passing vacuously.
    assert np.any(existing["tob_revenue_oasdi"] > 0)
    assert np.any(np.isclose(payroll, COMBINED_RATE * CAP, rtol=0, atol=TOLERANCE))

    # 5. Differential: a fresh simulation that never calculates the new
    # outputs gives the same existing outputs.
    fresh = Simulation(situation=situation)
    for name in EXISTING:
        np.testing.assert_array_equal(
            np.asarray(fresh.calculate(name, YEAR)), existing[name], err_msg=name
        )
