from policyengine_us.model_api import *


class wv_low_income_earned_income_exclusion_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the West Virginia low-income earned income exclusion"
    defined_for = StateCode.WV
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)

        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.low_income_earned_income_exclusion

        return federal_agi <= p.income_threshold[filing_status]
