from policyengine_us.model_api import *


class il_ccap_protective_care_override(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Illinois CCAP protective child care copay exemption override"
    documentation = "Whether the family qualifies for an Illinois protective child care copayment exemption not captured by generic homelessness or protective-services inputs."
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=54862"
