from policyengine_us.model_api import *


class dc_ccsp_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for DC Child Care Subsidy Program (CCSP)"
    definition_period = MONTH
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=8"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        eligible_child = person("dc_ccsp_eligible_child", period)
        has_eligible_child = spm_unit.any(eligible_child)
        asset_eligible = spm_unit("dc_ccsp_asset_eligible", period)
        income_eligible = spm_unit("dc_ccsp_income_eligible", period)
        income_test_waived = spm_unit("dc_ccsp_income_test_waived", period)
        qualified_activity_or_need_eligible = spm_unit(
            "dc_ccsp_qualified_activity_or_need_eligible", period
        )
        return (
            has_eligible_child
            & asset_eligible
            & (income_eligible | income_test_waived)
            & qualified_activity_or_need_eligible
        )
