from policyengine_us.model_api import *


class ky_ktap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Kentucky K-TAP"
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        income_eligible = spm_unit("ky_ktap_income_eligible", period)
        resource_eligible = spm_unit("ky_ktap_resource_eligible", period)
        return demographic_eligible & income_eligible & resource_eligible
