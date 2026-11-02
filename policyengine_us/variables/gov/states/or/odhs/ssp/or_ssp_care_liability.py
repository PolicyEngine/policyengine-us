from policyengine_us.model_api import *


class or_ssp_care_liability(Variable):
    value_type = float
    entity = Person
    label = "Oregon SSP care liability during a temporary absence"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.OR
    reference = (
        "https://ch461rules.odhs.oregon.gov/rules/461-155-0630.pdf#page=2",
        # PDF pages 1, 3-4
        "https://ch461rules.odhs.oregon.gov/rules/461-160-0620.pdf#page=1",
    )
    documentation = "Liability owed under OAR 461-160-0620 during an approved temporary absence from a community-based care facility. Leave at 0 when none is owed."
