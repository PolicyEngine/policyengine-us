from policyengine_us.model_api import *


class ia_fip_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP resources eligible"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.41.pdf#page=16"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.dhs.fip.resources
        current_recipient = spm_unit("is_tanf_enrolled", period)
        limit = where(
            current_recipient,
            p.recipient_limit,
            p.applicant_limit,
        )
        resources = spm_unit("spm_unit_assets", period.this_year)
        return resources <= limit
