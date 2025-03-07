from policyengine_us.model_api import *


class state_sales_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "State sales tax"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate.state_sales_tax_table
        # Clip the tax unit size to be between 1 and 6, following the form.
        TAX_UNIT_SIZE_CAP = 6
        tax_unit_size = tax_unit("tax_unit_size", period)
        capped_unit_size = max_(min_(tax_unit_size, TAX_UNIT_SIZE_CAP), 1)
        income_bracket = max_(
            tax_unit("state_sales_tax_income_bracket", period), 1
        )
        state_code = tax_unit.household("state_code", period)
        return p.tax[state_code][capped_unit_size][income_bracket]
