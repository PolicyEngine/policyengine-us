from policyengine_us.model_api import *


class ne_child_care_subsidy_categorical_waived(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy income and asset tests waived"
    defined_for = StateCode.NE
    reference = (
        "https://dhhs.ne.gov/Child%20Care%20Documents/ACF-118%20CCDF%20FFY%202025-2027%20For%20Nebraska%20-%20APPROVED.pdf#page=19",
        "https://dhhs.ne.gov/Child%20Care%20Documents/ACF-118%20CCDF%20FFY%202025-2027%20For%20Nebraska%20-%20APPROVED.pdf#page=23",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        foster = person("is_in_foster_care", period)
        # State Plan section 2.2.2(f)-(g) and 392 NAC 001.32 extend the
        # waiver beyond foster care to protective-services cases.
        protective = person("receives_or_needs_protective_services", period.this_year)
        return spm_unit.sum(foster | protective) > 0
