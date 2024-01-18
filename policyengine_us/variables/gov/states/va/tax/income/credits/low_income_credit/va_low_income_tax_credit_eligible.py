from policyengine_us.model_api import *


class va_low_income_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Virginia Low Income Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        # Criteria 1: Not qualified to claim EITC if anyone in the tax unit claimed any of the following:
        p = parameters(
            period
        ).gov.states.va.tax.income.credits.eitc.low_income_tax
        program_eligible = add(tax_unit, period, p.ineligible_programs) == 0

        # Criteria 2: Not qualified to claim EITC if the filier is claimed as a dependent on another taxpayer's return

        head_is_not_dependent_elsewhere = ~tax_unit(
            "head_is_dependent_elsewhere", period
        )

        return program_eligible & head_is_not_dependent_elsewhere
