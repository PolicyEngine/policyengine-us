from policyengine_us.model_api import *


class state_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "State property tax credit (legacy compatibility alias)"
    documentation = (
        "Deprecated legacy compatibility alias for taxsim_state_property_tax_credit. "
        "Prefer taxsim_state_property_tax_credit for new code."
    )
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("taxsim_state_property_tax_credit", period)
