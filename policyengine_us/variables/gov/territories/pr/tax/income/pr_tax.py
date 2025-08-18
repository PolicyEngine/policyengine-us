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
        p = parameters(period).gov.territories.pr.tax.income
        net_taxable_income = tax_unit("pr_net_taxable_income", period)
        rate = p.rate.calc(net_taxable_income)
        base_amount = p.base_amount.calc(net_taxable_income)
        phase_out = (net_taxable_income - threshold) * rate
        return base_amount + phase_out
