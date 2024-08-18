from policyengine_us.model_api import *


class basic_income_phase_in(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic income phase-in"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.contrib.ubi_center.basic_income.phase_in
        earnings = tax_unit("tax_unit_earned_income", period)
        if p.include_ss_benefits_as_earnings:
            ss_benefits = tax_unit("tax_unit_social_security", period)
            earnings += ss_benefits
        if p.per_person:
            tax_unit_size = tax_unit("tax_unit_size", period)
            rate = p.rate * tax_unit_size
        else:
            rate = p.rate
        return rate * earnings
