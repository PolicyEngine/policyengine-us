from policyengine_us.model_api import *


class id_special_season_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho special seasonal rebate"
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.id.tax.income.credits.special_seasonal_rebate
        income_tax_before_credits = tax_unit(
            "id_income_tax_before_non_refundable_credits", period
        )
        percentage_credit = p.rate * income_tax_before_credits
        filing_status = tax_unit("filing_status", period)
        floor = p.floor[filing_status]
        return max_(percentage_credit, floor)
