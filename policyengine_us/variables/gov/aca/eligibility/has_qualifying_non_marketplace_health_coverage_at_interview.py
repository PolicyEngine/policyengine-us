from policyengine_us.model_api import *


class has_qualifying_non_marketplace_health_coverage_at_interview(Variable):
    value_type = bool
    entity = Person
    label = "Person has qualifying non-Marketplace health coverage at interview"
    definition_period = YEAR

    def formula(person, period, parameters):
        return (
            person(
                "qualifying_non_marketplace_health_coverage_type_count_at_interview",
                period,
            )
            > 0
        )
