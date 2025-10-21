from policyengine_us.model_api import *


class ga_itemizer_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia itemizer tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/georgia/2022/title-48/chapter-7/article-2/section-48-7-29-23/",
        # Definition of resident
        "https://law.justia.com/codes/georgia/2022/title-48/chapter-7/article-1/section-48-7-1/",
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        # Full-year and part-year residents who itemize their deductions
        # are entitled to a credit up to $300 per taxpayer
        # Joint filers have 2 taxpayers, all others have 1
        itemizes = tax_unit("tax_unit_itemizes", period)
        is_joint = tax_unit("tax_unit_is_joint", period)
        taxpayer_count = where(is_joint, 2, 1)
        p = parameters(period).gov.states.ga.tax.income.credits.itemizer
        return where(itemizes, p.amount * taxpayer_count, 0)
