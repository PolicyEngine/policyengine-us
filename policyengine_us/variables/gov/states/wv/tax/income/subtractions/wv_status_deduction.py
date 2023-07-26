from policyengine_us.model_api import *
import math


class wv_status_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia status deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#Page=25"
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        adjusted_gross_income = tax_unit("wv_agi", period)
        social_security_benefit = tax_unit(
            "wv_social_security_benefit", period
        )
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.social_security_benefit
        agi_limit = adjusted_gross_income <= p.income_limit[filing_status]
        return where(agi_limit, social_security_benefit, 0)
