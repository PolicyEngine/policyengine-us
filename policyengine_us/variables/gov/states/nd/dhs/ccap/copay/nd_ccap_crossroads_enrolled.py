from policyengine_us.model_api import *


class nd_ccap_crossroads_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    default_value = False
    label = "North Dakota CCAP family receives Crossroads services"
    documentation = (
        "Records whether this family receives Crossroads Program services in the "
        "month under CCAP manual 400-28-90-20. "
        "North Dakota waived these families' co-payments by October 1, 2011."
    )
    reference = "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_90_20.htm"
