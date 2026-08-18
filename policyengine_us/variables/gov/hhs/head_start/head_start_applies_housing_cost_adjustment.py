from policyengine_us.model_api import *


class head_start_applies_housing_cost_adjustment(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Head Start program applies the excessive housing cost adjustment"
    documentation = (
        "Whether the family's Head Start or Early Head Start program reduces "
        "gross income by excessive housing costs under 45 CFR 1302.12(i)(1)(ii) "
        "when determining income eligibility. The adjustment is at program "
        "discretion; set directly when the local program applies it."
    )
    definition_period = YEAR
    default_value = False
    reference = (
        "https://www.ecfr.gov/current/title-45/section-1302.12#p-1302.12(i)(1)(ii)"
    )
