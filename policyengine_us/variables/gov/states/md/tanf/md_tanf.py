from policyengine_us.model_api import *


class md_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = "https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0900-Financial-Eligibility/0907%20Income%20Calculation%20of%20Ineligible%20Member%20rev%2011.22.doc"

    def formula(spm_unit, period, parameters):
        # Maximum TANF amount received
        grant_standard = spm_unit("md_tanf_maximum_benefit", period)
        # SPM unit income after continuous deduction
        # Note: md_tanf_net_countable_income already includes all deductions
        income = spm_unit("md_tanf_net_countable_income", period)
        return max_(grant_standard - income, 0)
