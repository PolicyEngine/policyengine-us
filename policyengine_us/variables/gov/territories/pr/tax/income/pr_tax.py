from policyengine_us.model_api import *


class pr_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1004/subchapter-a/30061/"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.tax_rate
        net_income = tax_unit("pr_net_taxable_income", period)
        phase_out = (net_income - p.threshold.calc(net_income)) * p.rate.calc(
            net_income
        )
        return p.base_amount.calc(net_income) + phase_out
