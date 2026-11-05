"""Shared helpers for state EITC formulas that partially track federal rules."""

from policyengine_us.model_api import *
from policyengine_us.tools.section_911 import elects_section_911_exclusion


def eitc_filing_requirement_met(tax_unit, period):
    """Mirror the federal EITC filing condition used in the baseline formula."""

    is_required = tax_unit("tax_unit_is_required_to_file", period)
    files_voluntarily = tax_unit("would_file_taxes_voluntarily", period)
    would_file_for_credits = tax_unit(
        "would_file_if_eligible_for_refundable_credit", period
    )
    return is_required | files_voluntarily | would_file_for_credits


def eitc_section_911_eligible(tax_unit, period):
    """26 U.S.C. 32(c)(1)(C): no EITC for anyone claiming section 911 benefits.

    State credits that recompute a federal-style EITC waive only the federal
    rules they name (age, SSN, separate filing), so this one still applies.
    """

    return ~elects_section_911_exclusion(tax_unit, period)


def eitc_filing_status_eligible(
    tax_unit, period, parameters, separate_filer_eligible=None
):
    """Apply IRC 32(d), optionally using a state's frozen exception switch.

    The switch enables the separated-spouse exception, rather than making
    every separate filer eligible. Once enabled, the exception also governs
    separated head-of-household filers, who are married under IRC 7703(a)
    unless separated under a decree (IRC 7703(a)(2)).
    Qualifying children are counted before identification requirements:
    IRC 32(c)(3)(D) limits the credit schedule, not the separated-spouse
    exception in IRC 32(d)(2)(B).
    """

    if separate_filer_eligible is None:
        separate_filer_eligible = parameters(
            period
        ).gov.irs.credits.eitc.eligibility.separate_filer
    filing_status = tax_unit("filing_status", period)
    statuses = filing_status.possible_values
    separate = filing_status == statuses.SEPARATE
    if not separate_filer_eligible:
        return ~separate

    person = tax_unit.members
    # From 2021, IRC 32(d)(2)(A) determines marital status under IRC 7703(a)
    # only, so a separated filer whom IRC 7703(b) lets file as head of
    # household is still married for the EITC and needs the same exception.
    # is_separated on the head or spouse is the model's married-but-apart
    # indicator; head_of_household_eligible reads it for the 7703(b) route.
    separated_head_of_household = (
        filing_status == statuses.HEAD_OF_HOUSEHOLD
    ) & tax_unit.any(
        person("is_tax_unit_head_or_spouse", period) & person("is_separated", period)
    )
    # IRC 7703(a)(2): "an individual legally separated from his spouse under
    # a decree of divorce or of separate maintenance shall not be considered
    # as married." Such a unit is unmarried for IRC 32(d)(2)(A), so neither
    # the separate-return nor the separated head-of-household branch needs
    # the exception.
    separated_under_decree = tax_unit.any(
        person("is_tax_unit_head_or_spouse", period)
        & person("is_separated_under_decree", period)
    )
    needs_exception = (separate | separated_head_of_household) & ~separated_under_decree
    has_resident_qualifying_child = tax_unit.any(
        person("is_eitc_qualifying_child", period)
        & person("eitc_child_lived_with_taxpayer_more_than_half_year", period)
    )
    meets_separation_conditions = tax_unit(
        "eitc_spouses_lived_apart_last_six_months", period
    ) | tax_unit("eitc_legal_separation_and_apart_at_year_end", period)
    return ~needs_exception | (
        has_resident_qualifying_child & meets_separation_conditions
    )


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
    # IRC 32(c)(1)(A)(ii)(II) applies the childless age test to the filer or,
    # on a joint return, either spouse, never to a dependent, matching the
    # federal eitc_demographic_eligible.
    is_filer_or_spouse = ~person("is_tax_unit_dependent", period)
    return has_child | tax_unit.any(
        is_filer_or_spouse & (age >= min_age) & (age <= max_age)
    )


def calculate_eitc_phase_out_start(
    tax_unit,
    period,
    eitc_parameters,
    child_count,
):
    """Return the EITC phase-out starting point for a chosen law version."""

    phase_out_start = eitc_parameters.phase_out.start.calc(child_count)
    phase_out_start += tax_unit(
        "tax_unit_is_joint", period
    ) * eitc_parameters.phase_out.joint_bonus.calc(child_count)
    return phase_out_start


def calculate_eitc_amount_from_parameters(
    tax_unit,
    period,
    eitc_parameters,
    child_count,
):
    """Calculate the uncapped EITC amount under a chosen parameter set."""

    earnings = tax_unit("eitc_earned_income", period)
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
    section_911_eligible = eitc_section_911_eligible(tax_unit, period)
    return (
        calculate_eitc_amount_from_parameters(
            tax_unit, period, eitc_parameters, child_count
        )
        * demographic_eligible
        * filer_identification_eligible
        * investment_income_eligible
        * filing_status_eligible
        * section_911_eligible
        * is_filer
        * takes_up_eitc
    )
