from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    calculate_eitc_like_amount,
    eitc_filing_requirement_met,
    eitc_filing_status_eligible,
)


class dc_base_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC EITC under the federal-incorporation base path"
    unit = USD
    definition_period = YEAR
    # SSN requirement flows from IRC section 32(c)(1)(F) and 32(m); D.C. Law
    # 23-149 lifts that restriction for the ITIN-inclusive dc_eitc.
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04",  # DC EITC base statute
        "https://www.law.cornell.edu/uscode/text/26/32",  # IRC 32 SSN-rule incorporation
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
        meets_eitc_id = person("meets_eitc_identification_requirements", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        filer_meets_id = tax_unit.sum(is_head_or_spouse & ~meets_eitc_id) == 0
        qualifying_child = (
            person("is_qualifying_child_dependent", period) & meets_eitc_id
        )
        child_count = tax_unit.sum(qualifying_child)
        has_qualifying_child = child_count > 0
        p = parameters(period).gov.states.dc.tax.income.credits

        with_child_eitc = (
            calculate_eitc_like_amount(
                tax_unit,
                period,
                parameters,
                child_count,
                has_qualifying_child,
                filer_meets_id,
            )
            * p.eitc.with_children.match
        )

        min_age = parameters.gov.irs.credits.eitc.eligibility.age.min(period)
        max_age = parameters.gov.irs.credits.eitc.eligibility.age.max(period)
        age_eligible = is_head_or_spouse & (age >= min_age) & (age <= max_age)
        without_child_eligible = (
            filer_meets_id
            & ~has_qualifying_child
            & tax_unit.any(age_eligible)
            & tax_unit("eitc_investment_income_eligible", period)
            & eitc_filing_status_eligible(tax_unit, period, parameters)
            & eitc_filing_requirement_met(tax_unit, period)
            & tax_unit("takes_up_eitc", period)
        )
        without_child_phased_in = without_child_eligible * tax_unit(
            "eitc_phased_in", period
        )
        earnings = tax_unit("tax_unit_earned_income", period)
        agi = tax_unit("adjusted_gross_income", period)
        greater_of = max_(earnings, agi)
        excess = max_(0, greater_of - p.eitc.without_children.phase_out.start)
        without_child_phase_out = excess * p.eitc.without_children.phase_out.rate
        without_child_eitc = max_(0, without_child_phased_in - without_child_phase_out)

        return where(has_qualifying_child, with_child_eitc, without_child_eitc)
