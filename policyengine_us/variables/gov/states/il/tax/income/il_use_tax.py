from policyengine_us.model_api import *


class il_use_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL use tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        # Tiered amount if income below a threshold, otherwise a percentage of AGI.
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.states.il.tax.income.use_tax
        return p.amount.calc(agi) + (p.rate.calc(agi) * agi)
