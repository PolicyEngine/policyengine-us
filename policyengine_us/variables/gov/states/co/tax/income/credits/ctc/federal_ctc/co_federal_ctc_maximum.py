from policyengine_us.model_api import *


class co_federal_ctc_maximum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum CTC replicated to include the Colorado limitations"
    unit = USD
    documentation = "Maximum value of the Child Tax Credit, before phase-out."
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

    adds = ["co_federal_ctc_child_individual_maximum"]
