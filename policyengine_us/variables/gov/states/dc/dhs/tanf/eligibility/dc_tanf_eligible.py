from policyengine_us.model_api import *


class dc_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for DC Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = "https://dhs.dc.gov/service/tanf-district-families"
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        basic = spm_unit("dc_tanf_basic_eligibility_requirements", period)
        enrolled = spm_unit("is_tanf_enrolled", period)
        meets_work = spm_unit("dc_tanf_meets_work_requirements", period)
        # Non-enrolled applicants must meet work requirements for eligibility.
        # Enrolled recipients who fail get a benefit sanction instead (in dc_tanf).
        return basic & (enrolled | meets_work)
