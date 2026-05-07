"""Shared helpers for state EITC formulas that partially track federal rules."""

from policyengine_us.model_api import *


def eitc_filing_requirement_met(tax_unit, period):
    """Mirror the federal EITC filing condition used in the baseline formula."""

    is_required = tax_unit("tax_unit_is_required_to_file", period)
    files_voluntarily = tax_unit("would_file_taxes_voluntarily", period)
    would_file_for_credits = tax_unit(
        "would_file_if_eligible_for_refundable_credit", period
    )
    return is_required | files_voluntarily | would_file_for_credits


def eitc_filing_status_eligible(
    tax_unit, period, parameters, separate_filer_eligible=None
):
    """Apply the federal EITC separate-filer rule unless a state overrides it."""

    if separate_filer_eligible is None:
        separate_filer_eligible = (
            parameters.gov.irs.credits.eitc.eligibility.separate_filer(period)
        )
    if separate_filer_eligible:
        return True
    filing_status = tax_unit("filing_status", period)
    return filing_status != filing_status.possible_values.SEPARATE


def calculate_eitc_demographic_eligibility(
    tax_unit, period, eitc_parameters, child_count=None
):
    """Apply the EITC child-count and age tests using a specific law version."""

    if child_count is None:
        child_count = tax_unit("eitc_child_count", period)
    has_child = child_count > 0
    person = tax_unit.members
    age = person("age", period)
    student = person("is_full_time_student", period)
    min_age = where(
        student,
        eitc_parameters.eligibility.age.min_student,
        eitc_parameters.eligibility.age.min,
    )
    max_age = eitc_parameters.eligibility.age.max
    return has_child | tax_unit.any((age >= min_age) & (age <= max_age))


def calculate_eitc_phase_out_start(
    tax_unit,
    period,
    eitc_parameters,
    child_count,
):
    """Return the EITC phase-out starting point for a chosen law version."""

    phase_out_start = eitc_parameters.phase_out.start.calc(child_count)
    phase_out_start += tax_unit("tax_unit_is_joint", period) * eitc_parameters.phase_out.joint_bonus.calc(
        child_count
    )
    return phase_out_start


def calculate_eitc_amount_from_parameters(
    tax_unit,
    period,
    eitc_parameters,
    child_count,
):
    """Calculate the uncapped EITC amount under a chosen parameter set."""

    earnings = tax_unit("filer_adjusted_earnings", period)
    agi = tax_unit("adjusted_gross_income", period)
    maximum = eitc_parameters.max.calc(child_count)
    phase_in_rate = eitc_parameters.phase_in_rate.calc(child_count)
    phased_in = min_(maximum, earnings * phase_in_rate)
    phase_out_start = calculate_eitc_phase_out_start(
        tax_unit, period, eitc_parameters, child_count
    )
    phase_out_rate = eitc_parameters.phase_out.rate.calc(child_count)
    reduction = max_(0, max_(earnings, agi) - phase_out_start) * phase_out_rate
    limitation = max_(0, maximum - reduction)
    return min_(phased_in, limitation)


def calculate_eitc_max_agi_limit(
    tax_unit,
    period,
    eitc_parameters,
    child_count,
):
    """Return the maximum AGI at which a positive EITC remains available."""

    phase_out_start = calculate_eitc_phase_out_start(
        tax_unit, period, eitc_parameters, child_count
    )
    return phase_out_start + eitc_parameters.max.calc(
        child_count
    ) / eitc_parameters.phase_out.rate.calc(child_count)


def calculate_eitc_like_amount(
    tax_unit,
    period,
    parameters,
    child_count,
    demographic_eligible,
    filer_identification_eligible,
    separate_filer_eligible=None,
    eitc_parameters=None,
    investment_income_eligible=None,
):
    """Calculate a federal-style EITC amount using state-specific child/ID rules."""

    if eitc_parameters is None:
        eitc_parameters = parameters(period).gov.irs.credits.eitc
    if investment_income_eligible is None:
        investment_income_eligible = (
            tax_unit("eitc_relevant_investment_income", period)
            <= eitc_parameters.phase_out.max_investment_income
        )
    filing_status_eligible = eitc_filing_status_eligible(
        tax_unit, period, parameters, separate_filer_eligible
    )
    is_filer = eitc_filing_requirement_met(tax_unit, period)
    takes_up_eitc = tax_unit("takes_up_eitc", period)
    return (
        calculate_eitc_amount_from_parameters(
            tax_unit, period, eitc_parameters, child_count
        )
        * demographic_eligible
        * filer_identification_eligible
        * investment_income_eligible
        * filing_status_eligible
        * is_filer
        * takes_up_eitc
    )
