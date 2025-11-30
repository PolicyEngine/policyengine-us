from policyengine_us.model_api import *


class pr_gradual_adjustment_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Puerto Rico gradual adjustment eligibility"
    definition_period = YEAR
    defined_for = StateCode.PR
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=3"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.gradual_adjustment
        net_taxable_income = tax_unit("pr_net_taxable_income", period)

        return net_taxable_income > p.threshold
