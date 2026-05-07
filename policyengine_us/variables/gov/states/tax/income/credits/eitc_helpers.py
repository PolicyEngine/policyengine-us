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


def calculate_eitc_like_amount(
    tax_unit,
    period,
    parameters,
    child_count,
    demographic_eligible,
    filer_identification_eligible,
    separate_filer_eligible=None,
):
    """Calculate a federal-style EITC amount using state-specific child/ID rules."""

    eitc = parameters(period).gov.irs.credits.eitc
    earnings = tax_unit("filer_adjusted_earnings", period)
    agi = tax_unit("adjusted_gross_income", period)
    maximum = eitc.max.calc(child_count)
    phase_in_rate = eitc.phase_in_rate.calc(child_count)
    phased_in = min_(maximum, earnings * phase_in_rate)
    phase_out_start = eitc.phase_out.start.calc(child_count)
    phase_out_start += tax_unit("tax_unit_is_joint", period) * eitc.phase_out.joint_bonus.calc(
        child_count
    )
    phase_out_rate = eitc.phase_out.rate.calc(child_count)
    reduction = max_(0, max_(earnings, agi) - phase_out_start) * phase_out_rate
    limitation = max_(0, maximum - reduction)
    investment_income_eligible = tax_unit("eitc_investment_income_eligible", period)
    filing_status_eligible = eitc_filing_status_eligible(
        tax_unit, period, parameters, separate_filer_eligible
    )
    is_filer = eitc_filing_requirement_met(tax_unit, period)
    takes_up_eitc = tax_unit("takes_up_eitc", period)
    return (
        min_(phased_in, limitation)
        * demographic_eligible
        * filer_identification_eligible
        * investment_income_eligible
        * filing_status_eligible
        * is_filer
        * takes_up_eitc
    )
