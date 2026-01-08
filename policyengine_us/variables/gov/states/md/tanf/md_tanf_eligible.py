from policyengine_us.model_api import *


class md_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Maryland TCA eligible"
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.03.aspx"

    def formula(spm_unit, period, parameters):
        has_children = spm_unit("md_tanf_count_children", period) > 0
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        return has_children & demographic_eligible
