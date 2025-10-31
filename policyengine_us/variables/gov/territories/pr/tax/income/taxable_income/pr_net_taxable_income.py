from policyengine_us.model_api import *


class pr_net_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico net taxable income"
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=2"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        agi = tax_unit("pr_agi", period)
        exemptions = tax_unit("pr_exemptions", period)
        deductions = tax_unit("pr_deductions", period)
        return max_(0, agi - exemptions - deductions)
