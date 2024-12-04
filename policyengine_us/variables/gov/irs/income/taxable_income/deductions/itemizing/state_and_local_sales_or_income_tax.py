from policyengine_us.model_api import *


class state_and_local_sales_or_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "State and local sales or income tax"
    unit = USD

    def formula(tax_unit, period, parameters):
        # Only sales or income tax can be itemized, but not both.
        income_tax = add(
            tax_unit, period, ["state_withheld_income_tax", "local_income_tax"]
        )
        sales_tax = add(
            tax_unit, period, ["state_sales_tax", "local_sales_tax"]
        )
        return max_(income_tax, sales_tax)
