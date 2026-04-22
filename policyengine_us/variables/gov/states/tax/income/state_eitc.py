from policyengine_us.model_api import *


class state_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "State earned income tax credit (legacy compatibility alias)"
    documentation = (
        "Deprecated legacy compatibility alias for taxsim_state_eitc. "
        "Prefer taxsim_state_eitc for new code."
    )
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("taxsim_state_eitc", period)
