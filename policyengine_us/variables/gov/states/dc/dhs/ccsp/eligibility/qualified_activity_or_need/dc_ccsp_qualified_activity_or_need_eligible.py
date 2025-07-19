from policyengine_us.model_api import *


class dc_ccsp_qualified_activity_or_need_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for DC Child Care Subsidy Program (CCSP) due to qualified activity or need"
    definition_period = MONTH
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=8"

    def formula(spm_unit, period, parameters):
        qualified_activity_eligible = spm_unit(
            "dc_ccsp_qualified_activity_eligible", period
        )
        qualified_need_eligible = spm_unit(
            "dc_ccsp_qualified_need_eligible", period
        )
        return qualified_activity_eligible | qualified_need_eligible
