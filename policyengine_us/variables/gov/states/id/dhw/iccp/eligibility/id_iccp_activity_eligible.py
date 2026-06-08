from policyengine_us.model_api import *


class id_iccp_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Activity eligible for the Idaho Child Care Program"
    defined_for = StateCode.ID
    reference = "https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=13"

    def formula(spm_unit, period, parameters):
        return spm_unit("meets_ccdf_activity_test", period.this_year)
