from policyengine_us.model_api import *


class az_wood_stove_conversion_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona wood stove conversion subtraction"
    unit = USD
    documentation = "https://www.azleg.gov/ars/43/01027.htm"
    reference = "A.R.S. 43-1027 - Wood Stoves, Fireplaces"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.subtractions.wood_stove

        expenses = tax_unit("az_wood_stove_conversion_expense", period)

        max_amount = p.max_amount

        return min_(expenses, max_amount)
