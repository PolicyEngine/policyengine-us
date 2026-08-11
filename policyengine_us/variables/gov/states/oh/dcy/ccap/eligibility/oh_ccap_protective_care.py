from policyengine_us.model_api import *


class oh_ccap_protective_care(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family receives Ohio CCAP protective care"
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5180:6-1-02"

    def formula(spm_unit, period, parameters):
        return (
            add(
                spm_unit,
                period.this_year,
                ["receives_or_needs_protective_services"],
            )
            > 0
        )
