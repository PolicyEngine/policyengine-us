from policyengine_us.model_api import *


class ri_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island AGI Subtractions"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%201041%20Schedule%20M_w.pdf#page=1"
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.agi.subtractions
        total_subtractions = add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
