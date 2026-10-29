"""Shared helpers for state EITC formulas that partially track federal rules."""

from policyengine_us.model_api import *
from policyengine_us.tools.period_branch import get_branch_for_period
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    NEUTRALIZED_BEHAVIORAL_RESPONSE_VARIABLES,
)
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


SSN_LIMITATION_WAIVED_BRANCH = "eitc_without_ssn_limitation"


def keep_return_as_filed(branch, tax_unit, period):
    """Give `branch` the AGI and behavioral responses of `tax_unit`'s simulation.

    A state credit that recomputes the federal EITC takes the amounts on the
    federal return as filed. The Maryland booklet (Instruction 18) has an ITIN
    filer calculate "the federal earned income credit disregarding the SSN
    requirement", and the Maine worksheet has the filer complete a "pro forma"
    federal EIC worksheet; the federal worksheet takes AGI from the return
    (2024 Form 1040 instructions, Worksheet A, line 3: "Enter the amount from
    Form 1040 or 1040-SR, line 11"). As inputs, the branch's AGI and
    responses cannot move with the changed credit, through the itemization
    election (whose 2020-2021 charitable deduction is above the line) or a
    response measured on the branch's own marginal rates. The credit is then
    computed on actual earnings, capital gains and AGI.
    """

    person = tax_unit.members
    variables = branch.tax_benefit_system.variables
    for variable in NEUTRALIZED_BEHAVIORAL_RESPONSE_VARIABLES:
        if not variables[variable].is_neutralized:
            branch.set_input(variable, period, person(variable, period))
    branch.set_input(
        "adjusted_gross_income", period, tax_unit("adjusted_gross_income", period)
    )


def federal_eitc_tax_unit(tax_unit, period):
    """The tax units whose federal EITC variables apply their state's 32(m) rule.

    Section 32(m) limits the taxpayer identification number that 32(c)(1)(E)
    (filer and spouse) and 32(c)(3)(D) (qualifying children) require to a
    Social Security number valid for employment. A state that waives 32(m)
    accepts any taxpayer identification number: an individual taxpayer
    identification number or a Social Security number of any kind (has_tin).
    state_eitc_ssn_limitation_waived says which tax units' states waive it:
    every Maryland return from 2020, and from 2021 a Maine return whose filer
    files a federal return.

    When the waiver changes no one's identification, this is `tax_unit`
    itself. Otherwise it is the same tax units in a branch where
    eitc_ssn_limitation_waived equals state_eitc_ssn_limitation_waived, so
    the EITC variables read from it (eitc, eitc_child_count, eitc_phased_in,
    ...) are those that would be allowable but for 32(m) for the waived tax
    units and the federal ones for the rest, under the same formulas,
    structural reforms and inputs (take-up among them). Every state credit
    gives the branch the same flag, so the branch doesn't depend on which
    state's credit the simulation calculates first. The flag reaches only the
    EITC's identification test (eitc_identification_accepted): the recovery
    rebate credits and other rules that require a valid Social Security
    number keep meets_eitc_identification_requirements, in the branch and in
    the itemization branches it creates. The branch takes the AGI and
    behavioral responses of the return as filed (keep_return_as_filed).

    Setting an input on the branch drops what the branch holds that may have
    been calculated from the replaced value, and setting it to the value the
    branch already reads as an input drops nothing (policyengine-core's
    Simulation.set_input), so the inputs are set on every call. The branch is
    created again for each period (get_branch_for_period), from the parent as
    it stands then, so it reads that period's inputs even when they changed
    after an earlier period's branch was created.
    """

    waived = tax_unit("state_eitc_ssn_limitation_waived", period)
    person = tax_unit.members
    valid_ssn = person("meets_eitc_identification_requirements", period)
    newly_accepted = tax_unit.project(waived) & person("has_tin", period) & ~valid_ssn
    if not newly_accepted.any():
        return tax_unit
    branch = get_branch_for_period(
        tax_unit.simulation, SSN_LIMITATION_WAIVED_BRANCH, period
    )
    keep_return_as_filed(branch, tax_unit, period)
    branch.set_input("eitc_ssn_limitation_waived", period, waived)
    return branch.tax_unit


def pro_forma_federal_eitc(federal, period, branch_name, eligible):
    """The final federal eitc of the tax units `federal`, with `eligible` as
    its eligibility and no take-up or filing condition.

    Maryland's childless credit and Maine's 18-24 expansion compute the
    federal credit for filers the federal age floor excludes. Evaluating the
    final eitc formula, with eitc_eligible set to the pro forma's own
    eligibility, carries through any reform of that formula, such as the
    individual EITC's AGI limit or a reform that neutralizes eitc. The pro
    formas have never applied take-up, the filing condition or the
    separate-filer rule, so takes_up_eitc and would_file_taxes_voluntarily are
    true and `eligible` leaves out the separate-filer rule. `federal` is the
    tax units federal_eitc_tax_unit returns, so a waiver of 32(m) carries
    through, and the branch takes their AGI and behavioral responses.
    """

    branch = get_branch_for_period(federal.simulation, branch_name, period)
    keep_return_as_filed(branch, federal, period)
    true = np.ones(federal.count, dtype=bool)
    branch.set_input("eitc_eligible", period, eligible)
    branch.set_input("takes_up_eitc", period, true)
    branch.set_input("would_file_taxes_voluntarily", period, true)
    return branch.tax_unit("eitc", period)


def eitc_filing_status_eligible(
    tax_unit, period, parameters, separate_filer_eligible=None
):
    """Apply the federal EITC separate-filer rule unless a state overrides it."""

    if separate_filer_eligible is None:
        separate_filer_eligible = parameters(
            period
        ).gov.irs.credits.eitc.eligibility.separate_filer
    filing_status = tax_unit("filing_status", period)
    return separate_filer_eligible | (
        filing_status != filing_status.possible_values.SEPARATE
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
    return has_child | tax_unit.any((age >= min_age) & (age <= max_age))


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
