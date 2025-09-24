from policyengine_us.model_api import *


class id_2022_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho 2022 rebate"
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.id.tax.income.credits["2022_rebate"]
        income_tax_before_credits = tax_unit(
            "id_income_tax_before_non_refundable_credits", period
        )
        percentage_credit = p.rate * income_tax_before_credits
        floor = add(tax_unit, period, ["id_2022_rebate_floor"])
        return max_(percentage_credit, floor)
