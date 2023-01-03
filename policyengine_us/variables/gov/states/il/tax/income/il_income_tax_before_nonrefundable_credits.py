from policyengine_us.model_api import *


class il_income_tax_before_nonrefundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL income tax before credits"
    unit = USD
    definition_period = YEAR

    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        recapture_of_investment_credit = tax_unit(
            "recapture_of_investment_credit", period
        )
        rate = parameters(period).gov.states.il.tax.income.rate

        return (
            tax_unit("il_taxable_income", period) * rate
            + recapture_of_investment_credit
        )
