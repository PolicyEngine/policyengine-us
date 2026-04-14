from policyengine_us.model_api import *


class state_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "State child and dependent care tax credit (legacy compatibility alias)"
    documentation = (
        "Deprecated legacy compatibility alias for taxsim_state_cdcc. "
        "Prefer taxsim_state_cdcc for new code."
    )
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("taxsim_state_cdcc", period)
