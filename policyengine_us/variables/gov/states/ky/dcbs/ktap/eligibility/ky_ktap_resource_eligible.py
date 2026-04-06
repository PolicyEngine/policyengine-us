from policyengine_us.model_api import *


class ky_ktap_resource_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Kentucky K-TAP due to resources"
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.dcbs.ktap.eligibility
        resources = spm_unit("spm_unit_assets", period.this_year)
        return resources <= p.resource_limit
