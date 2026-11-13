"""Monthly countable income under SSI methodology."""

from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


def ssi_countable_income(person, period, parameters, parent_deemed=None):
    """Apply SSI exclusions with an optional parental-deeming override."""
    # Apply the student exclusion to the individual's earned income.
    pre_reduction_earned_income = person("ssi_marital_earned_income", period)
    blind_disabled_working_student_income = person(
        "ssi_blind_or_disabled_working_student_exclusion", period
    )
    earned_income = max_(
        pre_reduction_earned_income - blind_disabled_working_student_income,
        0,
    )

    # SSI's marital income variables already combine eligible spouses' income.
    unearned_income = person("ssi_marital_unearned_income", period)
    if parent_deemed is None:
        parent_deemed = person(
            "ssi_unearned_income_deemed_from_ineligible_parent_monthly", period
        )

    # Count ISM before exclusions under 20 CFR 416.1140.
    ism = person("ssi_in_kind_support_and_maintenance_monthly", period)

    total_unearned = unearned_income + parent_deemed + ism

    personal_countable = _apply_ssi_exclusions(
        earned_income,
        total_unearned,
        parameters,
        period,
        monthly=True,
    )

    # Each eligible spouse takes half the couple's countable income.
    both_eligible = person("ssi_couple_computation_applies", period)

    # Add deemed spouse income after excluding the individual's own income.
    spousal_deemed = person("ssi_income_deemed_from_ineligible_spouse_monthly", period)

    # State programs can apply SSI income rules with different immigration tests.
    is_aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)

    return where(
        ~is_aged_blind_disabled,
        0,
        where(
            both_eligible,
            personal_countable / 2,
            personal_countable + spousal_deemed,
        ),
    )
