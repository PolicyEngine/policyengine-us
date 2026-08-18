from policyengine_us.model_api import *


class il_ccap_protective_care_copay_exempt(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Illinois CCAP protective child care copay exempt"
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=54862"

    def formula(spm_unit, period, parameters):
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        receives_protective_services = (
            add(
                spm_unit,
                period.this_year,
                ["receives_or_needs_protective_services"],
            )
            > 0
        )
        override = spm_unit("il_ccap_protective_care_override", period)
        return is_homeless | receives_protective_services | override
