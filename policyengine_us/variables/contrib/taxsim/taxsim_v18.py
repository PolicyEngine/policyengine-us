from policyengine_us.model_api import *


class taxsim_v18(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable income in TAXSIM"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("taxable_income", period)
