from policyengine_us.model_api import *


class nd_ccap_has_tanf_eligible_child(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    default_value = False
    label = "North Dakota CCAP family has a TANF-eligible child"
    documentation = (
        "Records whether this family includes a child who qualifies for TANF. "
        "North Dakota preserves the ineligible Kinship Care caretaker's "
        "co-payment waiver in this situation under CCAP manual 400-28-90-20."
    )
    reference = "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_90_20.htm"
