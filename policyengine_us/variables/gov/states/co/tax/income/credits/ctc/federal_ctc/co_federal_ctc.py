from policyengine_us.model_api import *


class co_federal_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Child Tax Credit replicated to include the Colorado limitations"
    unit = USD
    documentation = "Total value of the non-refundable and refundable portion of the Child Tax Credit."
    definition_period = YEAR
    reference = (
        # C.R.S. 39-22-129. Child tax credit - legislative declaration - definitions.
        "https://law.justia.com/codes/colorado/title-39/specific-taxes/income-tax/article-22/part-1/section-39-22-129/",
        # 2022 Colorado Child Tax Credit
        "https://tax.colorado.gov/sites/tax/files/documents/DR_0104CN_2022.pdf#page=1",
        # Colorado Individual Income Tax Filing Guide - Instructions for Select Credits from the DR 0104CR - Line 1 Child Tax Credit
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=16",
    )
    defined_for = StateCode.CO

    adds = ["co_refundable_ctc", "co_non_refundable_ctc"]
