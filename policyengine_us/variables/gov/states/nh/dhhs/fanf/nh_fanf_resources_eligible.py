from policyengine_us.model_api import *


class nh_fanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Hampshire FANF resources eligible"
    definition_period = YEAR
    reference = (
        "https://www.dhhs.nh.gov/fam_htm/",
        "https://www.dhhs.nh.gov/sr_htm/html/sr_97-03_dated_02_97.htm",
    )
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        # NOTE: One vehicle per adult is excluded regardless of value.
        p = parameters(period).gov.states.nh.dhhs.fanf.resources
        resources = spm_unit("spm_unit_assets", period)
        return resources <= p.limit
