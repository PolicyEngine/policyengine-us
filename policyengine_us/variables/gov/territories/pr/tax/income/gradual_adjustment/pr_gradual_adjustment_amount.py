from policyengine_us.model_api import *


class pr_gradual_adjustment_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico gradual adjustment amount"
    documentation = (
        "An additional amount added to tax amount for high income filers."
    )
    unit = USD
    definition_period = YEAR
    defined_for = "pr_gradual_adjustment_eligible"
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=3"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.gradual_adjustment
        net_taxable_income = tax_unit("pr_net_taxable_income", period)
        amount = (net_taxable_income - p.threshold) * p.rate
        exemptions = tax_unit("pr_exemptions", period)
        limit = p.adjustment_limit_basis + p.exemption_rate * exemptions

        return min_(amount, limit)
