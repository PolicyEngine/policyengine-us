from openfisca_us.model_api import *


class md_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD CTC"
    definition_period = YEAR
    unit = USD
    documentation = "Maryland Child Tax Credit"
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-751-effective-until-712026-tax-credit-for-qualified-child"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        "Md. Code, Tax-Gen. § 10-751 (c) The amount of the credit allowed under subsection (b) of this section for a qualified child shall be reduced, but not below zero, by the amount of any federal child tax credit claimed against the federal income tax for the qualified child under § 24 of the Internal Revenue Code. (d) If the credit allowed under this section in any taxable year exceeds the State income tax for that taxable year, the taxpayer may claim a refund in the amount of the excess."
        md_ctc = tax_unit("md_ctc_without_federal", period)
        federal_non_refundable_ctc = tax_unit("non_refundable_ctc", period)
        return max_(md_ctc - federal_non_refundable_ctc, 0)
