from policyengine_us.model_api import *


class md_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Maryland TANF eligible"
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = "https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0300-Technical-Eligibility/0300%20Technical%20Eligibility%20Overview%20rev%2011.22.doc"

    def formula(spm_unit, period, parameters):
        has_children = spm_unit("md_tanf_count_children", period) > 0
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        return has_children & demographic_eligible
