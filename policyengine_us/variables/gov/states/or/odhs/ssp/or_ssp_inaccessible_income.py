from policyengine_us.model_api import *


class or_ssp_inaccessible_income(Variable):
    value_type = float
    entity = Person
    label = "Oregon SSP income inaccessible due to incapacity"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.OR
    reference = (
        "https://ch461rules.odhs.oregon.gov/rules/461-140-0040.pdf#page=4",
        # PDF pages 2-3
        "https://ch461rules.odhs.oregon.gov/rules/461-155-0630.pdf#page=2",
    )
    documentation = "Income that an individual determined eligible for community-based care or nursing facility services cannot access due to incapacity while a legal or financial representative is being established, approved as unavailable for up to three months under OAR 461-140-0040(5)(e)(D). Leave at 0 otherwise, including for in-home services."
