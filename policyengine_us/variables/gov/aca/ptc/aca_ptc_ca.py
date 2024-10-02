from policyengine_us.model_api import *


class aca_ptc_ca(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA premium tax credit for taxunit in California"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/36B"
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        plan_cost = tax_unit("aca_slspc_ca", period)
        income = tax_unit("aca_magi", period)
        applicable_figure = tax_unit("aca_ptc_phase_out_rate", period)
        return max_(0, plan_cost - income * applicable_figure)
