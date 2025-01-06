from policyengine_us.model_api import *


class ca_state_supplement_food_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "California SSI state supplement food allowance"
    unit = USD
    definition_period = MONTH
    defined_for = "ca_state_supplement_food_allowance_eligible"
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.state_supplement.payment_standard
        is_married = spm_unit("spm_unit_is_married", period)
        aged_disabled_count = spm_unit(
            "ca_state_supplement_aged_disabled_count", period
        )
        # Food allowance amount
        return where(
            is_married & (aged_disabled_count == 2),
            p.allowance.food.married,
            p.allowance.food.single,
        )
