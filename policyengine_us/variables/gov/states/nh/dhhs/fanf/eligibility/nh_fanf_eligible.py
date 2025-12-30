from policyengine_us.model_api import *


class nh_fanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Hampshire FANF eligible"
    definition_period = MONTH
    reference = (
        "https://gc.nh.gov/rsa/html/xii/167/167-79.htm",
        "https://www.dhhs.nh.gov/sr_htm/html/sr_97-03_dated_02_97.htm",
    )
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        income_eligible = spm_unit("nh_fanf_income_eligible", period)
        resources_eligible = spm_unit(
            "nh_fanf_resources_eligible", period.this_year
        )
        return (
            demographic_eligible
            & immigration_eligible
            & income_eligible
            & resources_eligible
        )
