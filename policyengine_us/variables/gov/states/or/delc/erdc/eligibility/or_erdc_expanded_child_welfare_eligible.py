from policyengine_us.model_api import *


class or_erdc_expanded_child_welfare_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for Oregon ERDC through Expanded Child Welfare"
    defined_for = StateCode.OR
    reference = (
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0025"
    )

    def formula(spm_unit, period, parameters):
        # OAR 414-175-0025(1)(b)(B) grants Expanded Child Welfare eligibility
        # for use of Child Welfare protective services; we track foster care
        # receipt but not Child Abuse Prevention or Family Reunification
        # services, so those pathways are omitted.
        return add(spm_unit, period, ["is_in_foster_care"]) > 0
