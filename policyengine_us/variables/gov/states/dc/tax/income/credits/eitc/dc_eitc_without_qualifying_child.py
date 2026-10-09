from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    eitc_filing_requirement_met,
    eitc_filing_status_eligible,
    eitc_section_911_eligible,
)


class dc_eitc_without_qualifying_child(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC EITC without qualifying children"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04",  # (f)
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        # From 2023, D.C. Code 47-1806.04(f)(1)(D)(ii) extends the credit to
        # ITIN filers, overriding the IRC 32(m) Social Security number rule.
        person = tax_unit.members
        age = person("age", period)
        has_tin = person("has_tin", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        filer_has_tin = tax_unit.sum(is_head_or_spouse & ~has_tin) == 0
        p = parameters(period).gov.states.dc.tax.income.credits.eitc
        filer_meets_identification = where(
            p.itin_eligible,
            filer_has_tin,
            tax_unit("filer_meets_eitc_identification_requirements", period),
        )
        min_age = parameters.gov.irs.credits.eitc.eligibility.age.min(period)
        max_age = parameters.gov.irs.credits.eitc.eligibility.age.max(period)
        age_eligible = is_head_or_spouse & (age >= min_age) & (age <= max_age)
        # (f)(1)(C) is limited to an individual without a qualifying child.
        no_qualifying_child = ~tax_unit("dc_eitc_has_qualifying_child", period)
        us_eligible = (
            filer_meets_identification
            & no_qualifying_child
            & tax_unit.any(age_eligible)
            & tax_unit("eitc_investment_income_eligible", period)
            & eitc_filing_status_eligible(tax_unit, period, parameters)
            & eitc_section_911_eligible(tax_unit, period)
            & eitc_filing_requirement_met(tax_unit, period)
            & tax_unit("takes_up_eitc", period)
        )
        us_eitc = us_eligible * tax_unit("eitc_phased_in", period)
        # phase out us_eitc for income above DC phase-out start threshold
        earnings = tax_unit("tax_unit_earned_income", period)
        us_agi = tax_unit("adjusted_gross_income", period)
        greater_of = max_(earnings, us_agi)
        dc = parameters(period).gov.states.dc.tax.income.credits
        excess = max_(0, greater_of - dc.eitc.without_children.phase_out.start)
        dc_phase_out_amount = excess * dc.eitc.without_children.phase_out.rate
        return max_(0, us_eitc - dc_phase_out_amount)
