from policyengine_us.model_api import *


class ga_itemizer_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia itemizer tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/georgia/2022/title-48/chapter-7/article-2/section-48-7-29-23/"
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        # Full-year and part-year residents who itemize their deductions
        # are entitled to a credit up to $300 per taxpayer
        itemizes = tax_unit("tax_unit_itemizes", period)
        taxpayer_count = tax_unit("head_spouse_count", period)
        p = parameters(period).gov.states.ga.tax.income.credits.itemizer
        return where(itemizes, p.amount * taxpayer_count, 0)
