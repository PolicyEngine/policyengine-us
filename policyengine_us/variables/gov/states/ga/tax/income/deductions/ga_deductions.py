from policyengine_us.model_api import *


class ga_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia deductions"
    unit = USD
    reference = (
        # (a)(1) ties itemization to the federal choice.
        "https://law.justia.com/codes/georgia/2022/title-48/chapter-7/article-2/section-48-7-27/",
        # Page 12 states:
        # "If you use the standard deduction on your Federal
        #  return, you must use the Georgia standard deduction on
        #  your Georgia return."
        # Page 13 states:
        # "If you itemize deductions on your Federal return, or if you
        #  are married filing separate and your spouse itemizes deductions,
        #  you must itemize deductions on your Georgia return."
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download",
    )
    definition_period = YEAR
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        sd = tax_unit("ga_standard_deduction", period)
        # 48-7-27(a)(1) states:
        # "Either the sum of all itemized nonbusiness deductions used in computing
        #  such taxpayer’s federal taxable income or..."
        p = parameters(period).gov.irs.deductions
        itemized = add(tax_unit, period, p.itemized_deductions)
        return where(itemizes, itemized, sd)
