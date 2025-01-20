from policyengine_us.model_api import *


class sc_sales_and_use_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina sales and use tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.sc.tax.sales_and_use

        # base amount

        # sales and use tax rate with eligible exclusion
        eligible = tax_unit("sc_sales_and_use_exclusion_eligible", period)
        exclusion = p.exclusion.percentage * eligible
        rate_applied = p.general - exclusion

        # return base amount * rate_applied
