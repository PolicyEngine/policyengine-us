from policyengine_us.model_api import *


class pr_regular_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico regular tax before credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR
    reference = "https://hacienda.pr.gov/sites/default/files/inst_individuals_2023.pdf#page=19"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.regular_tax
        gross_income = tax_unit("pr_gross_income", period)
        total_normal_tax = add(
            tax_unit, period, ["pr_normal_tax", "pr_gradual_adjustment_amount"]
        )

        return total_normal_tax * p.percentage.calc(gross_income)
