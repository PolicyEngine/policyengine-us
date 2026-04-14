from policyengine_us.model_api import *


class state_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "State taxable income (legacy compatibility alias)"
    documentation = (
        "Deprecated legacy compatibility alias for taxsim_state_taxable_income. "
        "Prefer taxsim_state_taxable_income for new code."
    )
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("taxsim_state_taxable_income", period)
