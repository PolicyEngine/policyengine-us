from policyengine_us.model_api import *


class va_low_income_tax_credit_program_eligibility(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Qualification for the Virginia Low Income Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        # Criteria 1: Not qualified to claim EITC if anyone in the tax unit claimed any of the following:
        age_blind = tax_unit("va_age_blind_exemption", period)
        age = tax_unit("va_age_deduction", period)
        military = tax_unit("va_military_benefic_substraction", period)
        federal = tax_unit("va_federal_state_employees_substraction", period)
        criteria_1 = (age_blind + age + military + federal) < 0

        # Criteria 2: Not qualified to claim EITC if the filier is claimed as a dependent on another taxpayer's return

        criteria_2 = ~tax_unit("head_is_dependent_elsewhere", period)

        return criteria_1 & criteria_2
