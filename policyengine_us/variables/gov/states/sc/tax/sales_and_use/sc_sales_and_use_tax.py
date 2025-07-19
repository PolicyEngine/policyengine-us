from policyengine_us.model_api import *


class sc_sales_and_use_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina sales and use tax"
    unit = USD
    reference = "https://dor.sc.gov/forms-site/Forms/ST3.pdf#page=2"
    definition_period = YEAR
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.sc.tax.sales_and_use

        # base amount
        taxable_sales_and_purchases = tax_unit(
            "sc_sales_and_purchases_proceeds", period
        )

        # sales and use tax rate with eligible exclusion
        eligible = tax_unit("sc_sales_and_use_exclusion_eligible", period)
        exclusion = p.exclusion.percentage * eligible
        applicable_rate = p.rate - exclusion

        # return base amount * applicable_rate
        return taxable_sales_and_purchases * applicable_rate
