from policyengine_us.model_api import *


class ca_child_care_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Child Care Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        tanf_eligible = spm_unit("ca_tanf_eligible", period)
        age_eligible = spm_unit("ca_child_care_age_eligible", period)
        work_requirement = spm_unit("ca_child_care_work_requirement", period)

        return tanf_eligible & age_eligible & work_requirement
