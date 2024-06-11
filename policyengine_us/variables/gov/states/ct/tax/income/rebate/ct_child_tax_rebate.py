from policyengine_us.model_api import *


class ct_child_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut child tax rebate"
    unit = USD
    definition_period = YEAR
    defined_for = "ct_child_tax_rebate_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.tax.income.rebate

        count_dependents = tax_unit("tax_unit_count_dependents", period)
        rebate = count_dependents * p.amount

        return min_(p.cap, rebate)
