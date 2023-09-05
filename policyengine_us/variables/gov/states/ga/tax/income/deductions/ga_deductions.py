from policyengine_us.model_api import *


class ga_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia deductions"
    unit = USD
    reference = (
        "https://law.justia.com/codes/georgia/2022/title-48/chapter-7/article-2/section-48-7-27/",
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download",
    )
    definition_period = YEAR
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        sd = tax_unit("ga_standard_deduction", period)
        itemized = tax_unit("itemized_deductions_less_salt", period)
        return where(itemizes, itemized, sd)
