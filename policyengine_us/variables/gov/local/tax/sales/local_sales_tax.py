from policyengine_us.model_api import *


class local_sales_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Local sales tax"
    unit = USD

    def formula(tax_unit, period, parameters):
        # Until modeling the local sales tax table, estimate by multiplying by 0.2.
        return tax_unit("state_sales_tax", period) * 0.2
