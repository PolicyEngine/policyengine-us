from policyengine_us.model_api import *


class is_hud_dependent(Variable):
    value_type = bool
    entity = Person
    label = "HUD dependent"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/5.603"

    def formula(person, period, parameters):
        is_household_head = person("is_household_head", period)
        has_household_head = person.spm_unit.any(is_household_head)
        is_household_head_spouse = (
            person.tax_unit.any(is_household_head)
            & person("is_tax_unit_head_or_spouse", period)
            & ~is_household_head
        )
        is_hud_head_or_spouse = where(
            has_household_head,
            is_household_head | is_household_head_spouse,
            person("is_tax_unit_head_or_spouse", period),
        )
        meets_dependent_condition = (
            person("is_child", period)
            | person("is_disabled", period)
            | person("is_full_time_student", period)
        )
        is_foster = person("is_in_foster_care", period)
        return ~is_hud_head_or_spouse & meets_dependent_condition & ~is_foster
