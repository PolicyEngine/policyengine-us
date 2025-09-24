from policyengine_us.model_api import *


class ct_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.tax.income.subtractions
        total_subtractions = add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
