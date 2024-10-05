from policyengine_us.model_api import *


class co_non_refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Non-refundable Child Tax Credit replicated to include the Colorado limitations"
    unit = USD
    documentation = (
        "Total value of the non-refundable portion of the Child Tax Credit."
    )
    definition_period = YEAR
    reference = (
        # C.R.S. 39-22-129. Child tax credit - legislative declaration - definitions.
        "https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-129-child-tax-credit-legislative-declaration-definitions-repeal",
        # 2022 Colorado Child Tax Credit
        "https://tax.colorado.gov/sites/tax/files/documents/DR_0104CN_2022.pdf#page=1",
        # Colorado Individual Income Tax Filing Guide - Instructions for Select Credits from the DR 0104CR - Line 1 Child Tax Credit
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=16",
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        # follow 2022 DR 0104CN form and its instructions (in Book cited above):
        maximum = tax_unit("co_federal_ctc_maximum", period)  # Line 3
        limiting_tax_liability = tax_unit(
            "ctc_limiting_tax_liability", period
        )  # Line 4 - 6
        return min_(maximum, limiting_tax_liability)  # Line 7
