from policyengine_us.model_api import *


class nh_fanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Hampshire FANF resources eligible"
    definition_period = YEAR
    reference = (
        "https://www.dhhs.nh.gov/sr_htm/html/sr_97-03_dated_02_97.htm",
        "https://www.dhhs.nh.gov/fam_htm/newfam.htm",
        "https://www.dhhs.nh.gov/sites/g/files/ehbemt476/files/documents2/tanf-state-plan.pdf#page=25",
    )
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        # NOTE: One vehicle per adult is excluded regardless of value.
        # Resource limits differ for applicants ($1,000) vs recipients ($5,000 as of 07/01/22)
        p = parameters(period).gov.states.nh.dhhs.fanf.resources
        resources = spm_unit("spm_unit_assets", period)
        is_enrolled = spm_unit("is_tanf_enrolled", period)
        limit = where(is_enrolled, p.recipient_limit, p.applicant_limit)
        return resources <= limit
