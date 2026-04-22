from policyengine_us.model_api import *


class al_receives_elderly_disabled_medicaid_waiver(Variable):
    value_type = bool
    entity = Person
    label = "Alabama SSP recipient receives Elderly/Disabled Medicaid Waiver benefits"
    definition_period = MONTH
    defined_for = StateCode.AL
    default_value = False
    reference = "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=9"
    documentation = """
    Alabama's current optional SSP rules require post-October 1, 1986 private-home
    and foster-home cases to receive benefits under the Elderly/Disabled Medicaid
    Waiver Program.
    """
