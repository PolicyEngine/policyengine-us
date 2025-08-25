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
        p = parameters(period).gov.states.ny.otda.liheap.vulnerable
        person = spm_unit.members

        age = person("age", period)
        is_disabled = person("is_disabled", period)

        is_vulnerable = (
            (age >= p.elderly_age_threshold)
            | (age < p.child_age_threshold)
            | is_disabled
        )

        return spm_unit.any(is_vulnerable)
