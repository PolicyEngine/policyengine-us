import random
from itertools import product

import numpy as np

from policyengine_us import Simulation


PERIOD = "2026"
MORTGAGE_CASES = (
    ("no-debt", 0, 2023),
    ("post-tcja-uncapped", 600_000, 2023),
    ("post-tcja-capped", 900_000, 2023),
    ("pre-tcja-uncapped", 900_000, 2017),
    ("pre-tcja-capped", 1_500_000, 2017),
)


def _add_tax_unit(situation, name, joint, filers, mortgage, dependent_interest):
    members = []
    filer_names = []
    filer_indices = []
    dependent_indices = []

    for index, interest in enumerate(filers):
        person_name = f"{name}_filer_{index}"
        members.append(person_name)
        filer_names.append(person_name)
        filer_indices.append(len(situation["people"]))
        inputs = {
            "age": 45 - index,
            "is_tax_unit_head": index == 0,
            "is_tax_unit_spouse": index == 1,
            "is_tax_unit_dependent": False,
            **interest,
        }
        situation["people"][person_name] = {
            variable: {PERIOD: value} for variable, value in inputs.items()
        }

    for index, interest in enumerate(dependent_interest):
        person_name = f"{name}_dependent_{index}"
        members.append(person_name)
        dependent_indices.append(len(situation["people"]))
        inputs = {
            "age": 20 - index,
            "is_tax_unit_head": False,
            "is_tax_unit_spouse": False,
            "is_tax_unit_dependent": True,
            "home_mortgage_interest": interest,
        }
        situation["people"][person_name] = {
            variable: {PERIOD: value} for variable, value in inputs.items()
        }
        situation["marital_units"][person_name] = {"members": [person_name]}

    situation["tax_units"][name] = {
        "members": members,
        "filing_status": {PERIOD: "JOINT" if joint else "SINGLE"},
        **{variable: {PERIOD: value} for variable, value in mortgage.items()},
    }
    situation["households"][name] = {
        "members": members,
        "state_code": {PERIOD: "CA"},
    }
    situation["families"][name] = {"members": members}
    situation["spm_units"][name] = {"members": members}
    situation["marital_units"][name] = {"members": filer_names}
    return filer_indices, dependent_indices


def test_dependents_do_not_change_federal_mortgage_interest_or_allocations():
    """Matched returns conserve interest and allocate it only to filers.

    Varying dependents' own interest cannot change federal aggregates or
    filer allocations. Canonical payments determine proportional shares;
    structured fallback uses equal shares. No deduction outputs are supplied.
    """
    rng = random.Random(9950)
    situation = {
        entity: {}
        for entity in (
            "people",
            "tax_units",
            "households",
            "families",
            "spm_units",
            "marital_units",
        )
    }
    records = []

    for joint, source, mortgage_case, dependent_count in product(
        (False, True),
        ("canonical", "structured", "none"),
        MORTGAGE_CASES,
        (1, 2, 3),
    ):
        debt_label, balance, origination_year = mortgage_case
        filer_count = 2 if joint else 1
        filers = [
            {"home_mortgage_interest": rng.randint(1_000, 60_000)}
            if source == "canonical"
            else {}
            for _ in range(filer_count)
        ]
        if joint and source == "canonical" and dependent_count < 3:
            # Include head-only, spouse-only, and two-payer joint returns.
            filers[dependent_count - 1] = {}
        payments = np.array(
            [filer.get("home_mortgage_interest", 0) for filer in filers]
        )
        mortgage = {
            "first_home_mortgage_balance": balance,
            "first_home_mortgage_origination_year": origination_year,
        }
        if source == "structured":
            mortgage["first_home_mortgage_interest"] = rng.randint(1_000, 120_000)
        gross_interest = (
            payments.sum()
            if source == "canonical"
            else mortgage.get("first_home_mortgage_interest", 0)
        )
        expected_shares = (
            payments / payments.sum()
            if source == "canonical"
            else np.full(filer_count, 1 / filer_count)
        )
        label = (
            f"{'joint' if joint else 'single'}-{source}-{debt_label}"
            f"-{dependent_count}-dependents"
        )
        dependent_payments = [rng.randint(1, 200_000) for _ in range(dependent_count)]
        for suffix, dependent_interest in (
            ("before", [0] * dependent_count),
            ("after", dependent_payments),
        ):
            name = f"{label}-{suffix}"
            filer_indices, dependent_indices = _add_tax_unit(
                situation, name, joint, filers, mortgage, dependent_interest
            )
            records.append(
                (
                    name,
                    filer_indices,
                    dependent_indices,
                    gross_interest,
                    expected_shares,
                )
            )

    # One model construction covers 90 matched pairs, including both vintages.
    simulation = Simulation(situation=situation)
    gross = simulation.calculate("home_mortgage_interest_tax_unit", PERIOD)
    deductible = simulation.calculate("deductible_mortgage_interest_tax_unit", PERIOD)
    non_deductible = simulation.calculate(
        "non_deductible_mortgage_interest_tax_unit", PERIOD
    )
    person_deductible = simulation.calculate("deductible_mortgage_interest", PERIOD)
    person_non_deductible = simulation.calculate(
        "non_deductible_mortgage_interest", PERIOD
    )
    shares = simulation.calculate("home_mortgage_interest_share", PERIOD)

    for index, (name, filers, dependents, expected_gross, expected_shares) in enumerate(
        records
    ):
        np.testing.assert_allclose(
            gross[index], expected_gross, rtol=0, atol=0.01, err_msg=name
        )
        np.testing.assert_allclose(
            deductible[index] + non_deductible[index],
            gross[index],
            rtol=0,
            atol=0.01,
            err_msg=name,
        )
        assert deductible[index] >= 0, name
        assert non_deductible[index] >= 0, name
        np.testing.assert_allclose(
            shares[filers], expected_shares, rtol=0, atol=1e-7, err_msg=name
        )
        np.testing.assert_allclose(shares[dependents], 0, rtol=0, atol=0, err_msg=name)
        for person_values, tax_unit_values in (
            (person_deductible, deductible),
            (person_non_deductible, non_deductible),
        ):
            np.testing.assert_allclose(
                person_values[dependents], 0, rtol=0, atol=0, err_msg=name
            )
            np.testing.assert_allclose(
                person_values[filers].sum(),
                tax_unit_values[index],
                rtol=0,
                atol=0.01,
                err_msg=name,
            )
            np.testing.assert_allclose(
                person_values[filers],
                expected_shares * tax_unit_values[index],
                rtol=0,
                atol=0.01,
                err_msg=name,
            )
        np.testing.assert_allclose(
            person_deductible[filers] + person_non_deductible[filers],
            expected_shares * expected_gross,
            rtol=0,
            atol=0.01,
            err_msg=name,
        )

    for index in range(0, len(records), 2):
        name, before_filers, *_ = records[index]
        after_filers = records[index + 1][1]
        for variable, values in (
            ("gross", gross),
            ("deductible", deductible),
            ("non-deductible", non_deductible),
        ):
            np.testing.assert_allclose(
                values[index + 1],
                values[index],
                rtol=0,
                atol=0.01,
                err_msg=f"{name}: dependent inputs changed federal {variable}",
            )
        for variable, values in (
            ("deductible", person_deductible),
            ("non-deductible", person_non_deductible),
        ):
            np.testing.assert_allclose(
                values[after_filers],
                values[before_filers],
                rtol=0,
                atol=0.01,
                err_msg=f"{name}: dependent inputs changed filer {variable}",
            )
