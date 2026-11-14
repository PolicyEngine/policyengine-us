from policyengine_us.model_api import *


class nd_ccap_arsen_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    default_value = False
    label = "North Dakota CCAP family participates in ARSEN"
    documentation = (
        "Records whether this family participates in the Alternative Response "
        "for Substance Exposed Newborns program in the month. "
        "North Dakota waives its co-payment from April 1, 2021, under CCAP "
        "manual 400-28-90-20 and 400-28-55-30."
    )
    reference = (
        "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_90_20.htm",
        "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_55_30.htm",
    )
