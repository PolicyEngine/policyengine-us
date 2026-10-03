from policyengine_us.model_api import *


class md_qualifies_for_unmarried_childless_eitc(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Qualifies for the MD unmarried childless EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-704&enactments=false"  # (c)(3)
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        childless = tax_unit("eitc_child_count", period) == 0
        # Law says "individual".
        # Tax form instructions clarify that this means single/head/surviving spouse.
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        single_head_surviving_spouse = (
            (filing_status == filing_statuses.SINGLE)
            | (filing_status == filing_statuses.HEAD_OF_HOUSEHOLD)
            | (filing_status == filing_statuses.SURVIVING_SPOUSE)
        )
        return childless & single_head_surviving_spouse
