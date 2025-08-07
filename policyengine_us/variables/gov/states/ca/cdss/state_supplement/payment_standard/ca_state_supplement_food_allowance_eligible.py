from policyengine_us.model_api import *


class ca_state_supplement_food_allowance_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California SSI state supplement food allowance eligible"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        living_arrangements_allow_for_food_preparation = spm_unit.household(
            "living_arrangements_allow_for_food_preparation", period
        )
        aged_disabled_count = spm_unit(
            "ca_state_supplement_aged_disabled_count", period
        )
        return (
            aged_disabled_count > 0
        ) & ~living_arrangements_allow_for_food_preparation
