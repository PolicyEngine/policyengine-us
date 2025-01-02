from policyengine_us.model_api import *


class ca_state_supplement_food_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "California SSI state supplement food allowance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.state_supplement.payment_standard
        person = spm_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_married = spm_unit("spm_unit_is_married", period)
        # Aged or disabled amount
        is_disabled = person("is_disabled", period)
        age = person("monthly_age", period)
        is_aged = age >= p.aged_or_disabled.age_threshold
        aged_or_disabled = (is_aged | is_disabled) * head_or_spouse
        aged_disabled_count = spm_unit.sum(aged_or_disabled)
        # Food allowance amount
        living_arrangements_allow_for_food_preparation = spm_unit.household(
            "living_arrangements_allow_for_food_preparation", period
        )
        food_allowance_amount = select(
            [
                (is_married == 1) & (aged_disabled_count == 2),
                (is_married == 1) & (aged_disabled_count == 1),
                (aged_disabled_count == 1),
            ],
            [
                p.allowance.food.married,
                p.allowance.food.single,
                p.allowance.food.single,
            ],
            default=0,
        )
        return (
            ~living_arrangements_allow_for_food_preparation
            * food_allowance_amount
        )
