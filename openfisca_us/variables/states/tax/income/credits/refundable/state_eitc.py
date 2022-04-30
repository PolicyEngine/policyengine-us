from openfisca_us.model_api import *


class state_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "State Earned Income Tax Credit"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        match = parameters(
            period
        ).states.tax.income.credits.refundable.eitc.percent_match
        state = tax_unit.household("state_code_str", period)
        return tax_unit("eitc", period) * match[state]
