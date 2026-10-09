import random

import numpy as np

from policyengine_us import Simulation


PERIOD = "2026"
MORTGAGE_INPUTS = (
    "home_mortgage_interest",
    "mortgage_interest",
    "deductible_mortgage_interest",
    "non_deductible_mortgage_interest",
)
INTEREST_SOURCES = (
    "canonical",
    "canonical_with_supplied_deduction",
    "legacy",
    "reconstructed",
    "supplied_deduction",
    "structured",
    "none",
)


def _filer_interest(source, amount):
    if source in ("canonical", "canonical_with_supplied_deduction"):
        inputs = {"home_mortgage_interest": amount}
        if source == "canonical_with_supplied_deduction":
            inputs["deductible_mortgage_interest"] = amount / 2
        return inputs
    if source == "legacy":
        return {"mortgage_interest": amount}
    if source == "reconstructed":
        return {
            "deductible_mortgage_interest": amount / 2,
            "non_deductible_mortgage_interest": amount / 2,
        }
    if source == "supplied_deduction":
        return {"deductible_mortgage_interest": amount}
    return {}


def _add_tax_unit(situation, name, joint, filers, mortgage, dependents):
    members = []
    filer_names = []
    for index, interest in enumerate(filers):
        person_name = f"{name}_filer_{index}"
        members.append(person_name)
        filer_names.append(person_name)
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

    for index, interest in enumerate(dependents):
        person_name = f"{name}_dependent_{index}"
        members.append(person_name)
        inputs = {
            "age": 15 - index,
            "is_tax_unit_head": False,
            "is_tax_unit_spouse": False,
            "is_tax_unit_dependent": True,
            **interest,
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
        "state_code": {PERIOD: "HI"},
    }
    situation["families"][name] = {"members": members}
    situation["spm_units"][name] = {"members": members}
    situation["marital_units"][name] = {"members": filer_names}


def test_dependent_mortgage_inputs_never_change_hawaii_deduction():
    """Generate matched returns across every mortgage-interest source path."""
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
    labels = []

    for joint in (False, True):
        for source in INTEREST_SOURCES:
            # Exercise each person input alone, then arbitrary combinations.
            for sample in range(len(MORTGAGE_INPUTS) + 2):
                filers = [
                    _filer_interest(source, rng.randint(1_000, 150_000))
                    for _ in range(2 if joint else 1)
                ]
                debt = (0, 550_000, 1_100_000, 1_500_000, 3_000_000)[sample % 5]
                mortgage = {
                    "first_home_mortgage_balance": debt * 0.75,
                    "second_home_mortgage_balance": debt * 0.25,
                    "first_home_mortgage_origination_year": rng.choice(
                        (2010, 2017, 2023)
                    ),
                    "second_home_mortgage_origination_year": 2023,
                }
                if source == "structured":
                    mortgage["first_home_mortgage_interest"] = rng.randint(
                        1_000, 150_000
                    )
                    mortgage["second_home_mortgage_interest"] = rng.randint(
                        1_000, 150_000
                    )

                variables = (
                    (MORTGAGE_INPUTS[sample],)
                    if sample < len(MORTGAGE_INPUTS)
                    else MORTGAGE_INPUTS
                )
                dependents = [
                    {variable: rng.randint(1, 200_000) for variable in variables}
                    for _ in range(1 + sample % 3)
                ]
                label = f"{'joint' if joint else 'single'}-{source}-{sample}"
                labels.append(label)
                # Membership, filer inputs, and tax-unit debt remain identical.
                # Only the dependents' person-level mortgage inputs change.
                _add_tax_unit(
                    situation,
                    f"{label}-before",
                    joint,
                    filers,
                    mortgage,
                    [{} for _ in dependents],
                )
                _add_tax_unit(
                    situation,
                    f"{label}-after",
                    joint,
                    filers,
                    mortgage,
                    dependents,
                )

    # One vectorized calculation keeps the generated cases inexpensive.
    deduction = Simulation(situation=situation).calculate(
        "hi_mortgage_interest_deduction", PERIOD
    )
    before, after = deduction[::2], deduction[1::2]
    failures = [
        f"{label}: {old} -> {new}"
        for label, old, new in zip(labels, before, after)
        if abs(old - new) > 0.01
    ]
    np.testing.assert_allclose(
        after, before, rtol=0, atol=0.01, err_msg="\n".join(failures)
    )
