"""Premium conservation between Schedule A and the section 162(l) deduction.

IRC 162(l)(3) excludes premiums deducted under section 162(l) from medical
expenses under section 213. Hypothesis varies earnings caps, covered premium
subsets, direct/decomposed premium inputs, spouses, dependents and separate
tax units.
Premium inputs use payer attribution: a person's inputs include all premiums
that person paid, including family coverage regardless of who is covered.
The federal conservation properties generate deductions within the filers'
paid premiums; beneficiary-assigned inputs cannot establish that invariant.
The independent accounting invariant is that Schedule A's premium base plus
the self-employed health insurance deduction never exceeds premiums paid.
Non-premium medical expenses must remain available in full before the floor.

Examples use small vectorized simulations and a shared read-only reference
system. Supplied and computed subtotal scenarios use separate simulations to
preserve their input provenance. YAML covers the individual policy examples;
these properties check conservation across generated combinations and
filing-unit boundaries.
"""

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

PERIOD = "2025"


@pytest.fixture(scope="module")
def reference_system():
    return system


@st.composite
def person_expenses(draw):
    premiums = draw(st.integers(0, 25_000))
    direct = draw(st.booleans())
    self_employed = draw(st.booleans())
    covered = draw(st.integers(0, premiums)) if self_employed else 0
    # A direct premium can also exercise the default derivation of the SE
    # premium input. Decomposed premiums need the covered subset explicitly.
    if direct and draw(st.booleans()):
        covered = None
    return {
        "premiums": premiums,
        "other": draw(st.integers(0, 10_000)),
        "earnings": draw(st.integers(-25_000, 50_000)) if self_employed else 0,
        "self_employed": self_employed,
        "direct": direct,
        "covered": covered,
    }


units = st.lists(
    st.lists(person_expenses(), min_size=1, max_size=3),
    min_size=2,
    max_size=4,
)


@st.composite
def units_with_deduction(draw):
    members = draw(units)
    deductions = [
        # Payer attribution puts parent-paid family premiums on that parent.
        # The head's and spouse's deduction covers their paid premium pool. A
        # dependent's own SE deduction belongs on their separate return.
        draw(st.integers(0, sum(person["premiums"] for person in unit[:2])))
        for unit in members
    ]
    return members, deductions


def _simulation(members, reference_system, deductions=None):
    people, tax_units, households, marital_units = {}, {}, {}, {}
    for unit_index, unit in enumerate(members):
        names = []
        for person_index, person in enumerate(unit):
            name = f"person_{unit_index}_{person_index}"
            names.append(name)
            premium_variable = (
                "health_insurance_premiums"
                if person["direct"]
                else "health_insurance_premiums_without_medicare_part_b"
            )
            values = {
                "age": 12 if person_index == 2 else 40,
                "is_tax_unit_head": person_index == 0,
                "is_tax_unit_spouse": person_index == 1,
                "is_tax_unit_dependent": person_index == 2,
                "is_self_employed": person["self_employed"],
                "self_employment_income": person["earnings"],
                "medicare_enrolled": False,
                premium_variable: person["premiums"],
                "other_medical_expenses": person["other"],
            }
            if person["covered"] is not None:
                values["self_employed_health_insurance_premiums"] = person["covered"]
            people[name] = {
                variable: {PERIOD: value} for variable, value in values.items()
            }
        tax_unit = {"members": names}
        if deductions is not None:
            tax_unit["self_employed_health_insurance_ald"] = {
                PERIOD: deductions[unit_index]
            }
        tax_units[f"tax_unit_{unit_index}"] = tax_unit
        households[f"household_{unit_index}"] = {
            "members": names,
            "state_code": {PERIOD: "TX"},
        }
        marital_units[f"marital_unit_{unit_index}"] = {"members": names[:2]}
        for name in names[2:]:
            marital_units[f"dependent_marital_unit_{unit_index}"] = {"members": [name]}
    return Simulation(
        tax_benefit_system=reference_system,
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
            "marital_units": marital_units,
        },
    )


def _assert_conservation(members, simulation):
    paid = np.array([sum(person["premiums"] for person in unit) for unit in members])
    other = np.array([sum(person["other"] for person in unit) for unit in members])
    dependent_premiums = np.array(
        [sum(person["premiums"] for person in unit[2:]) for unit in members]
    )
    medical_base = simulation.calculate("itemized_medical_expenses", PERIOD)
    se_deduction = simulation.calculate("self_employed_health_insurance_ald", PERIOD)
    schedule_a_premium_use = medical_base - other

    # Neither the SE deduction nor a different filing unit can consume the
    # non-premium expenses. Check the bound separately from conservation.
    assert (schedule_a_premium_use >= 0).all()
    assert (schedule_a_premium_use >= dependent_premiums).all()
    assert (schedule_a_premium_use + se_deduction <= paid).all()
    # All premiums here are otherwise eligible: unused premiums remain in
    # Schedule A's base, even when earnings cap the SE deduction.
    np.testing.assert_array_equal(schedule_a_premium_use + se_deduction, paid)


EXAMPLE_UNITS = [
    [
        dict(
            premiums=6_000,
            other=500,
            earnings=1_000,
            self_employed=True,
            direct=True,
            covered=None,
        ),
        dict(
            premiums=2_000,
            other=300,
            earnings=5_000,
            self_employed=True,
            direct=False,
            covered=1_000,
        ),
        dict(
            premiums=12_000,
            other=200,
            earnings=15_000,
            self_employed=True,
            direct=True,
            covered=None,
        ),
    ],
    [
        dict(
            premiums=5_000,
            other=700,
            earnings=-2_000,
            self_employed=True,
            direct=True,
            covered=None,
        )
    ],
]


@settings(max_examples=12, deadline=None, derandomize=True)
@example(members=EXAMPLE_UNITS)
@given(members=units)
def test_premiums_are_not_duplicated_with_derived_se_deduction(
    reference_system, members
):
    _assert_conservation(members, _simulation(members, reference_system))


@settings(max_examples=12, deadline=None, derandomize=True)
@example(case=(EXAMPLE_UNITS, [8_000, 0]))
@given(case=units_with_deduction())
def test_premiums_are_not_duplicated_with_tax_unit_se_deduction(reference_system, case):
    members, deductions = case
    _assert_conservation(
        members, _simulation(members, reference_system, deductions=deductions)
    )


@st.composite
def nj_dependent_expenses(draw):
    return {
        "premiums": draw(st.integers(0, 25_000)),
        "other": draw(st.integers(0, 10_000)),
        # Independent person ALDs deliberately include amounts above the
        # person's paid medical premiums, as supported by separate SE inputs.
        "deduction": draw(st.integers(0, 50_000)),
    }


nj_units = st.lists(
    st.lists(nj_dependent_expenses(), min_size=2, max_size=4),
    min_size=2,
    max_size=4,
)


def _nj_simulation(members, reference_system):
    people, tax_units, households, marital_units = {}, {}, {}, {}
    for unit_index, unit in enumerate(members):
        parent = f"parent_{unit_index}"
        names = [parent]
        people[parent] = {"age": {PERIOD: 40}}
        marital_units[f"parent_marital_unit_{unit_index}"] = {"members": [parent]}
        for person_index, person in enumerate(unit):
            name = f"dependent_{unit_index}_{person_index}"
            names.append(name)
            people[name] = {
                variable: {PERIOD: value}
                for variable, value in {
                    "age": 17,
                    "is_tax_unit_dependent": True,
                    "medicare_enrolled": False,
                    "health_insurance_premiums": person["premiums"],
                    "other_medical_expenses": person["other"],
                    "self_employed_health_insurance_ald_person": person["deduction"],
                }.items()
            }
            marital_units[f"dependent_marital_unit_{unit_index}_{person_index}"] = {
                "members": [name]
            }
        tax_units[f"tax_unit_{unit_index}"] = {
            "members": names,
            "self_employed_health_insurance_ald": {PERIOD: 0},
            "nj_agi": {PERIOD: 0},
        }
        households[f"household_{unit_index}"] = {
            "members": names,
            "state_code": {PERIOD: "NJ"},
        }
    return Simulation(
        tax_benefit_system=reference_system,
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
            "marital_units": marital_units,
        },
    )


@settings(max_examples=12, deadline=None, derandomize=True)
@example(
    members=[
        [
            dict(premiums=0, other=0, deduction=1_000),
            dict(premiums=1_000, other=0, deduction=0),
        ],
        [
            dict(premiums=300, other=200, deduction=800),
            dict(premiums=500, other=100, deduction=0),
        ],
    ]
)
@given(members=nj_units)
def test_nj_excludes_each_dependents_deduction_only_from_their_own_premiums(
    reference_system, members
):
    simulation = _nj_simulation(members, reference_system)
    paid = np.array([sum(person["premiums"] for person in unit) for unit in members])
    other = np.array([sum(person["other"] for person in unit) for unit in members])
    deductions = np.array(
        [sum(person["deduction"] for person in unit) for unit in members]
    )
    person_exclusions = [
        [min(person["deduction"], person["premiums"]) for person in unit]
        for unit in members
    ]
    for unit, exclusions in zip(members, person_exclusions):
        assert all(
            0 <= exclusion <= person["premiums"]
            for person, exclusion in zip(unit, exclusions)
        )
    excluded = np.array([sum(exclusions) for exclusions in person_exclusions])
    nj_deduction = simulation.calculate("nj_medical_expense_deduction", PERIOD)
    actual_exclusion = paid + other + deductions - nj_deduction

    # C.54A:3-3(c)(3) excludes only amounts separately deducted. Each person's
    # exclusion is bounded before summation, so no ALD can consume a different
    # person's premiums. This property also covers ALDs above own paid costs.
    # https://pub.njleg.gov/bills/9899/PL99/222_.HTM
    assert (actual_exclusion >= 0).all()
    assert (actual_exclusion <= excluded).all()
    np.testing.assert_array_equal(actual_exclusion, excluded)
    np.testing.assert_array_equal(nj_deduction, paid + other + deductions - excluded)


# Flat strategies keep generation small while varying independent caller
# subtotals, component inputs, filing units and the senior-benefit gates.
state_expenses = st.fixed_dictionaries(
    {
        "premiums": st.tuples(*(st.integers(0, 25_000) for _ in range(3))),
        "other": st.tuples(*(st.integers(0, 30_000) for _ in range(3))),
        "direct": st.tuples(*(st.booleans() for _ in range(3))),
        "income": st.integers(0, 100_000),
        "age": st.sampled_from([64, 65, 80]),
        "filing_status": st.sampled_from(["SINGLE", "JOINT", "SEPARATE"]),
        "dependent_elsewhere": st.booleans(),
        "subtotal_mode": st.sampled_from(["derived", "supplied", "subtotal_only"]),
        "subtotal": st.one_of(
            st.integers(0, 100_000), st.sampled_from([27_999, 28_000, 28_001])
        ),
        "deduction": st.integers(-10_000, 75_000),
    }
)
state_units = st.lists(state_expenses, min_size=2, max_size=3)


def _state_case(**values):
    return {
        "premiums": (0, 0, 0),
        "other": (0, 0, 0),
        "direct": (True, True, True),
        "income": 30_000,
        "age": 65,
        "filing_status": "SINGLE",
        "dependent_elsewhere": False,
        "subtotal_mode": "derived",
        "subtotal": 0,
        "deduction": 1_000,
        **values,
    }


def _state_simulation(cases, reference_system, with_se_deduction):
    people, tax_units, households, marital_units = {}, {}, {}, {}
    expectations = {
        "nd_renters_refund_income": [],
        "nm_medical_expense_credit": [],
        "nm_medical_expense_exemption": [],
    }
    accounting = {
        "main_base": [],
        "gross": [],
        "other": [],
        "filer_premiums": [],
        "excluded": [],
        "applied_exclusion": [],
    }
    for case_index, case in enumerate(cases):
        joint = case["filing_status"] == "JOINT"
        person_indices = [0, 1, 2] if joint else [0, 2]
        subtotal_only = case["subtotal_mode"] == "subtotal_only"
        premiums = [0 if subtotal_only else case["premiums"][i] for i in person_indices]
        other = [0 if subtotal_only else case["other"][i] for i in person_indices]
        deduction = case["deduction"] if with_se_deduction else 0
        filer_premiums = premiums[0] + (premiums[1] if joint else 0)
        excluded = min(filer_premiums, max(0, deduction))
        gross = sum(premiums) + sum(other)
        supplied = case["subtotal_mode"] != "derived"
        # Caller subtotals are independent of their component inputs and SE
        # deduction. The oracle preserves the supplied amount exactly as main
        # does; only the computed path restores an applied federal exclusion.
        main_base = case["subtotal"] if supplied else gross
        senior_eligible = case["age"] >= 65 and main_base >= 28_000
        denominator = 2 if case["filing_status"] == "SEPARATE" else 1

        for state in ("ND", "NM"):
            unit_name = f"{state}_{case_index}"
            names = []
            for position, person_index in enumerate(person_indices):
                name = f"{unit_name}_person_{person_index}"
                names.append(name)
                premium_variable = (
                    "health_insurance_premiums"
                    if case["direct"][person_index]
                    else "health_insurance_premiums_without_medicare_part_b"
                )
                values = {
                    "age": case["age"]
                    if person_index == 0
                    else 40
                    if person_index == 1
                    else 17,
                    "is_tax_unit_head": person_index == 0,
                    "is_tax_unit_spouse": person_index == 1,
                    "is_tax_unit_dependent": person_index == 2,
                    "employment_income": case["income"] if person_index == 0 else 0,
                    "medicare_enrolled": False,
                    premium_variable: premiums[position],
                    "other_medical_expenses": other[position],
                }
                people[name] = {
                    variable: {PERIOD: value} for variable, value in values.items()
                }
                if person_index == 2:
                    marital_units[f"{unit_name}_dependent_marital_unit"] = {
                        "members": [name]
                    }
            marital_units[f"{unit_name}_marital_unit"] = {"members": names[:-1]}
            tax_unit = {
                "members": names,
                "self_employed_health_insurance_ald": {PERIOD: deduction},
                "filing_status": {PERIOD: case["filing_status"]},
                "head_is_dependent_elsewhere": {PERIOD: case["dependent_elsewhere"]},
            }
            if supplied:
                tax_unit["itemized_medical_expenses"] = {PERIOD: case["subtotal"]}
            tax_units[unit_name] = tax_unit
            households[unit_name] = {"members": names, "state_code": {PERIOD: state}}
            accounting["main_base"].append(main_base)
            accounting["gross"].append(gross)
            accounting["other"].append(sum(other))
            accounting["filer_premiums"].append(filer_premiums)
            accounting["excluded"].append(excluded)
            accounting["applied_exclusion"].append(0 if supplied else excluded)
            # This independent accounting oracle reproduces main's state
            # outputs from its paid-cost base rather than reading this head's
            # medical subtotal or excluded-premium calculations as expectations.
            expectations["nd_renters_refund_income"].append(
                max(0, case["income"] - main_base) if state == "ND" else 0
            )
            expectations["nm_medical_expense_credit"].append(
                2_800 / denominator
                if state == "NM" and senior_eligible and not case["dependent_elsewhere"]
                else 0
            )
            expectations["nm_medical_expense_exemption"].append(
                3_000 / denominator if state == "NM" and senior_eligible else 0
            )
    simulation = Simulation(
        tax_benefit_system=reference_system,
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
            "marital_units": marital_units,
        },
    )
    return simulation, expectations, accounting


def _assert_state_outputs(cases, reference_system, with_se_deduction):
    # Core records input provenance for an entire tax-unit vector. Keep supplied
    # and computed cases in separate simulations so computed rows are never
    # turned into supplied inputs by filling an otherwise partial input vector.
    for supplied in (False, True):
        same_provenance = [
            case for case in cases if (case["subtotal_mode"] != "derived") == supplied
        ]
        if not same_provenance:
            continue
        simulation, expectations, accounting = _state_simulation(
            same_provenance, reference_system, with_se_deduction
        )
        medical_base = simulation.calculate("itemized_medical_expenses", PERIOD)
        applied_exclusion = simulation.calculate(
            "itemized_medical_expenses_applied_exclusion", PERIOD
        )
        np.testing.assert_array_equal(
            applied_exclusion, accounting["applied_exclusion"]
        )
        np.testing.assert_array_equal(
            medical_base + applied_exclusion, accounting["main_base"]
        )
        if not supplied:
            excluded = simulation.calculate(
                "itemized_medical_expenses_excluded_premiums", PERIOD
            )
            # Computed Schedule A costs conserve the full paid amount when the
            # capped premium exclusion is restored. These bounds deliberately
            # do not constrain an independent caller-supplied subtotal.
            np.testing.assert_array_equal(excluded, accounting["excluded"])
            np.testing.assert_array_equal(medical_base + excluded, accounting["gross"])
            assert (excluded >= 0).all()
            assert (excluded <= np.array(accounting["filer_premiums"])).all()
            assert (medical_base >= np.array(accounting["other"])).all()
        for variable, expected in expectations.items():
            np.testing.assert_array_equal(
                simulation.calculate(variable, PERIOD), expected
            )


@settings(max_examples=12, deadline=None, derandomize=True)
@example(
    cases=[
        _state_case(subtotal_mode="subtotal_only", subtotal=6_500),
        _state_case(subtotal_mode="subtotal_only", subtotal=28_000),
        _state_case(
            premiums=(6_000, 0, 0),
            other=(22_000, 0, 0),
            subtotal_mode="supplied",
            subtotal=27_999,
        ),
        _state_case(premiums=(6_000, 0, 0), other=(21_999, 0, 0)),
        _state_case(premiums=(6_000, 0, 0), other=(22_001, 0, 0)),
    ]
)
@given(cases=state_units)
def test_state_paid_cost_bases_match_main_without_se_deduction(reference_system, cases):
    _assert_state_outputs(cases, reference_system, with_se_deduction=False)


@settings(max_examples=12, deadline=None, derandomize=True)
@example(
    cases=[
        _state_case(premiums=(6_000, 0, 0), other=(500, 0, 0)),
        _state_case(
            premiums=(6_000, 0, 0),
            other=(500, 0, 0),
            subtotal_mode="supplied",
            subtotal=6_500,
        ),
        _state_case(
            premiums=(6_000, 0, 0),
            other=(22_000, 0, 0),
            subtotal_mode="supplied",
            subtotal=27_999,
        ),
        _state_case(premiums=(1_000, 0, 0), subtotal_mode="supplied", subtotal=500),
        _state_case(premiums=(1_000, 0, 0), subtotal_mode="supplied", subtotal=0),
        _state_case(premiums=(6_000, 0, 0), other=(21_999, 0, 0), deduction=75_000),
        _state_case(subtotal_mode="subtotal_only", subtotal=28_000, deduction=75_000),
        _state_case(premiums=(0, 0, 28_000), deduction=75_000),
    ]
)
@given(cases=state_units)
def test_state_paid_cost_bases_preserve_main_inputs_with_se_deduction(
    reference_system, cases
):
    _assert_state_outputs(cases, reference_system, with_se_deduction=True)
