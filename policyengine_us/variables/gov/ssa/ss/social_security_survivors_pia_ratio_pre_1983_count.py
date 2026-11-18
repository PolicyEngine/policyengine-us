from policyengine_us.model_api import *


class social_security_survivors_pia_ratio_pre_1983_count(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    unit = "person"
    label = "Social Security survivors PIA-ratio pre 1983 count"
    documentation = (
        "Number of household members with the corresponding Person indicator. "
        "Population aggregation uses household weights once. If supplied Person "
        "weights differ within a household, use the Person indicator and its own "
        "Person weights for the authoritative weighted count."
    )

    def formula(household, period, parameters):
        return household.sum(
            household.members("social_security_survivors_pia_ratio_pre_1983", period)
        )
