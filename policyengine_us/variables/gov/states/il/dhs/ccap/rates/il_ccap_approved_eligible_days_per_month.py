from policyengine_us.model_api import *


class il_ccap_approved_eligible_days_per_month(Variable):
    value_type = int
    entity = Person
    definition_period = MONTH
    unit = "day"
    label = "Illinois CCAP approved eligible days per month"
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/onenetlibrary/12/documents/Forms/444708-202512_REV1.pdf#page=1"
