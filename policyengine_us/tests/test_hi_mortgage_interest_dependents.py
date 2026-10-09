import random

import numpy as np
import pytest

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
    "dataset_like",
    "dataset_like_dependent_only",
    "none",
)


def _filer_interest(source, amount):
    if source in (
        "canonical",
        "canonical_with_supplied_deduction",
        "dataset_like",
    ):
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


@pytest.mark.parametrize("reconstructed", (False, True))
def test_dependent_mortgage_inputs_never_change_hawaii_deduction(reconstructed):
    """Dependent payments cannot change deductions within a fixed source path.

    Dataset-like structured inputs equal all members' canonical payments;
    changing dependent payments and these matching totals leaves the filers'
    deduction unchanged. Canonical presence selects the filers' own amount,
    including zero, before any legacy gross or supplied-deduction fallback.
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
    labels = []
    expected = []
    sources = (
        ("reconstructed",)
        if reconstructed
        else tuple(source for source in INTEREST_SOURCES if source != "reconstructed")
    )

    for joint in (False, True):
        for source in sources:
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
                if reconstructed:
                    # Supplying a variable for one person installs a complete
                    # input vector, defaulting omitted persons to zero. Keep
                    # mortgage_interest calculated in this separate batch.
                    for inputs in dependents:
                        legacy_gross = inputs.pop("mortgage_interest", None)
                        if legacy_gross is not None and len(inputs) == 0:
                            inputs["deductible_mortgage_interest"] = legacy_gross / 2
                            inputs["non_deductible_mortgage_interest"] = (
                                legacy_gross / 2
                            )
                label = f"{'joint' if joint else 'single'}-{source}-{sample}"
                labels.append(label)
                before_dependents = [{} for _ in dependents]
                canonical_guard = "home_mortgage_interest" in variables and source in (
                    "legacy",
                    "reconstructed",
                    "supplied_deduction",
                    "structured",
                )
                if canonical_guard:
                    # Both sides already have canonical interest. Crossing
                    # from no canonical input to a positive one intentionally
                    # changes eligibility for the lower-priority fallbacks.
                    before_dependents = [
                        {"home_mortgage_interest": 1} for _ in dependents
                    ]

                filer_total = sum(sum(inputs.values()) for inputs in filers)
                if source == "canonical_with_supplied_deduction":
                    filer_total = sum(
                        inputs["home_mortgage_interest"] for inputs in filers
                    )
                if source == "structured":
                    filer_total = (
                        mortgage["first_home_mortgage_interest"]
                        + mortgage["second_home_mortgage_interest"]
                    )
                share = round(min(debt, 1_100_000) / debt, 3) if debt else 1
                expected.append(
                    0
                    if canonical_guard
                    else (
                        filer_total
                        if source == "supplied_deduction"
                        else filer_total * share
                    )
                )
                # Membership, filer inputs, and tax-unit debt remain identical.
                # Dataset-like exports additionally mirror all members'
                # canonical interest into the deprecated structured totals.
                for suffix, dependent_inputs in (
                    ("before", before_dependents),
                    ("after", dependents),
                ):
                    tax_unit_inputs = mortgage.copy()
                    if source in ("dataset_like", "dataset_like_dependent_only"):
                        all_member_total = sum(
                            inputs.get("home_mortgage_interest", 0)
                            for inputs in filers + dependent_inputs
                        )
                        tax_unit_inputs["first_home_mortgage_interest"] = (
                            all_member_total * 0.75
                        )
                        tax_unit_inputs["second_home_mortgage_interest"] = (
                            all_member_total * 0.25
                        )
                    _add_tax_unit(
                        situation,
                        f"{label}-{suffix}",
                        joint,
                        filers,
                        tax_unit_inputs,
                        dependent_inputs,
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
    np.testing.assert_allclose(before, expected, rtol=0, atol=0.02)
    np.testing.assert_allclose(after, expected, rtol=0, atol=0.02)
