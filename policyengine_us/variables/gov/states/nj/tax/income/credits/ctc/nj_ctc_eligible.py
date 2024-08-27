from policyengine_us.model_api import *


class nj_ctc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the New Jersey child tax credit"
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-17-1/"
        "https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2021/1040i.pdf#page=44"
        "https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2022/1040i.pdf#page=44"
        "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=46"
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Exclude married filing separately filers.
        filing_status = tax_unit("filing_status", period)
        return filing_status != filing_status.possible_values.SEPARATE
