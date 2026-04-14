from policyengine_us.model_api import *


class state_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "State adjusted gross income (legacy compatibility alias)"
    documentation = (
        "Deprecated legacy compatibility alias for taxsim_state_agi. "
        "Prefer taxsim_state_agi for new code."
    )
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("taxsim_state_agi", period)
