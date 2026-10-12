from policyengine_us.model_api import *


class ok_ccs_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oklahoma Child Care Subsidy eligible"
    definition_period = MONTH
    defined_for = StateCode.OK
    reference = "https://okrules.elaws.us/oac/340:40-7-1"

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["ok_ccs_eligible_child"]) > 0
        # Households receiving public assistance or Supplemental Security
        # Income are predetermined eligible; all other households must meet
        # the Appendix C-4 income threshold (OAC 340:40-7-1).
        predetermined = spm_unit("ok_ccs_predetermined_eligible", period)
        income_eligible = spm_unit("ok_ccs_income_eligible", period)
        activity_eligible = spm_unit("ok_ccs_activity_eligible", period)
        return (
            has_eligible_child & (predetermined | income_eligible) & activity_eligible
        )
