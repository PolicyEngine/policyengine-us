from policyengine_us.model_api import *


class wv_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia subtractions from the adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wv.tax.income.subtractions
        total_subtractions = add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
