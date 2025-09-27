from policyengine_us.model_api import *


class tx_ccs_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Texas CCS eligible"
    definition_period = MONTH
    reference = (
        "http://txrules.elaws.us/rule/title40_chapter809",
        "https://www.twc.texas.gov/programs/child-care",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Check all eligibility criteria
        income_eligible = spm_unit("tx_ccs_income_eligible", period)
        asset_eligible = spm_unit("tx_ccs_asset_eligible", period)
        work_eligible = spm_unit("tx_ccs_work_requirement_eligible", period)

        # Check if at least one child is age-eligible
        person = spm_unit.members
        age_eligible = person("tx_ccs_eligible_child", period)
        has_eligible_child = spm_unit.any(age_eligible)

        return (
            income_eligible
            & asset_eligible
            & work_eligible
            & has_eligible_child
        )
