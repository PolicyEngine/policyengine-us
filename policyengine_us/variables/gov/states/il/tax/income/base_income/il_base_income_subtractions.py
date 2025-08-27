from policyengine_us.model_api import *


class il_base_income_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL base income subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.base
        total_subtractions = add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
