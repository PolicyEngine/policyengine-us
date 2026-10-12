from policyengine_us.model_api import *


class medicaid_missing_claimant_fallback_person_count(Variable):
    value_type = float
    entity = Person
    label = "People represented using Medicaid MAGI missing-claimant fallback"
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("person_count", period) * person(
            "medicaid_uses_missing_claimant_fallback", period
        )
