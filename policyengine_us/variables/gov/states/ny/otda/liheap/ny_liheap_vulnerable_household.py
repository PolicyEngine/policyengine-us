from policyengine_us.model_api import *


class ny_liheap_vulnerable_household(Variable):
    value_type = bool
    entity = SPMUnit
    label = "NY LIHEAP household has vulnerable members"
    definition_period = YEAR
    defined_for = "ny_liheap_income_eligible"
    reference = "https://otda.ny.gov/programs/heap/"
    documentation = "Household contains members 60+ years old, children under 6, or permanently disabled individuals"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Check for elderly members (60+)
        age = person("age", period)
        has_elderly = spm_unit.any(age >= 60)

        # Check for young children (under 6)
        has_young_child = spm_unit.any(age < 6)

        # Check for disabled members
        is_disabled = person("is_disabled", period)
        has_disabled = spm_unit.any(is_disabled)

        return has_elderly | has_young_child | has_disabled
