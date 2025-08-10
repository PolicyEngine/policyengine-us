from policyengine_us.model_api import *


class de_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware dependent care credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        # Delaware matches the federal credit taken
        expenses = tax_unit("cdcc", period)
        rate = parameters(period).gov.states.de.tax.income.credits.cdcc.match
        return expenses * rate
