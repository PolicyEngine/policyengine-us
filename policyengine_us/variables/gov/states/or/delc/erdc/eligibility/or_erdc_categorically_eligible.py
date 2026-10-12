from policyengine_us.model_api import *


class or_erdc_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Categorically eligible for Oregon ERDC"
    defined_for = StateCode.OR
    reference = (
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0025"
    )

    def formula(spm_unit, period, parameters):
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        expanded_child_welfare = spm_unit(
            "or_erdc_expanded_child_welfare_eligible", period
        )
        return tanf_enrolled | expanded_child_welfare
