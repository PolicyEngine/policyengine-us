from policyengine_us.model_api import *


class co_leap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Colorado LEAP eligible household size"
    defined_for = StateCode.CO
    # PDF pages 29,51,55
    reference = (
        "https://drive.google.com/file/d/1G3XKsXyKoPZmsA5-P6NI6w3svP99xOZd/view#page=29"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.co.cdhs.leap.eligibility
        person = spm_unit.members
        qualified = person("is_citizen_or_legal_immigrant", period)
        foster = person("is_in_foster_care", period.first_month)
        # SPM membership approximates the energy-sharing economic unit;
        # kinship status and later changes in foster status are not represented.
        return min_(spm_unit.sum(qualified & ~foster), p.max_household_size)
