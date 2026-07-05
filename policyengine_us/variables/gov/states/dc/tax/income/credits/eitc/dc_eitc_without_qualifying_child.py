from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    eitc_filing_requirement_met,
    eitc_filing_status_eligible,
)


class dc_eitc_without_qualifying_child(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC EITC without qualifying children"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04",  # (f)
        # IRC 152(c)(3)(B) waives the qualifying-child age test for permanently and totally disabled individuals.
        "https://www.law.cornell.edu/uscode/text/26/152#c_3_B",
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        # D.C. Law 23-149 extends the EITC to ITIN filers, overriding the
        # federal IRC section 32 SSN-only identification rule.
        person = tax_unit.members
        age = person("age", period)
        has_tin = person("has_tin", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        filer_has_tin = tax_unit.sum(is_head_or_spouse & ~has_tin) == 0
        min_age = parameters.gov.irs.credits.eitc.eligibility.age.min(period)
        max_age = parameters.gov.irs.credits.eitc.eligibility.age.max(period)
        age_eligible = is_head_or_spouse & (age >= min_age) & (age <= max_age)
        # IRC 152(c)(3)(B) waives the age test for a permanently and totally
        # disabled dependent, so such a dependent is a qualifying child and
        # routes the unit to the with-children schedule.
        is_disabled_dependent = person("is_tax_unit_dependent", period) & person(
            "is_permanently_and_totally_disabled", period
        )
        qualifying_child = (
            person("is_qualifying_child_dependent", period) | is_disabled_dependent
        ) & has_tin
        no_qualifying_child = tax_unit.sum(qualifying_child) == 0
        us_eligible = (
            filer_has_tin
            & no_qualifying_child
            & tax_unit.any(age_eligible)
            & tax_unit("eitc_investment_income_eligible", period)
            & eitc_filing_status_eligible(tax_unit, period, parameters)
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
