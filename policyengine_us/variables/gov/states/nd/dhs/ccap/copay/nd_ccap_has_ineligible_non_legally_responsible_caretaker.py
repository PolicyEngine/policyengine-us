from policyengine_us.model_api import *


class nd_ccap_has_ineligible_non_legally_responsible_caretaker(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    default_value = False
    label = (
        "North Dakota CCAP family has an ineligible non-legally responsible caretaker"
    )
    documentation = (
        "Records whether an ineligible non-legally responsible caretaker needs "
        "child care for an activity in this TANF or Diversion family. "
        "North Dakota applies the co-payment under CCAP manual 400-28-90-20."
    )
    reference = "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_90_20.htm"
