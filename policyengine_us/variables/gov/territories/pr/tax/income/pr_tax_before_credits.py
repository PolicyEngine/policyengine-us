from policyengine_us.model_api import *


class pr_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico regular tax before credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR
    reference = "https://hacienda.pr.gov/sites/default/files/inst_individuals_2023.pdf#page=19"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income
        gross_income = tax_unit("pr_gross_income", period)
        tax = tax_unit("pr_tax", period)
        gradual_adjustment = tax_unit("pr_gradual_adjustment_amount", period)
        total_normal_tax = tax + gradual_adjustment

        return total_normal_tax * p.normal_tax_percent_reduction.calc(
            gross_income
        )
