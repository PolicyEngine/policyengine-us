from policyengine_us.model_api import *


class ca_child_care_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Child Care Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        tanf_eligible = spm_unit("ca_tanf_eligible", period)

        person = spm_unit.members
        resources_eligible = spm_unit("ca_tanf_resources_eligible", period)

        return demographic_eligible & income_eligible & resources_eligible
