from openfisca_us.model_api import *


class md_qualifies_for_single_childless_eitc(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Qualifies for the MD single childless EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"  # (c)(3)
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        childless = tax_unit("eitc_child_count", period) == 0
        # Law says "individual".
        # Tax form instructions clarify that this means single/head/widow.
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        single_head_widow = (
            (filing_status == filing_statuses.SINGLE)
            | (filing_status == filing_statuses.HEAD_OF_HOUSEHOLD)
            | (filing_status == filing_statuses.WIDOW)
        )
        return childless & single_head_widow
