from policyengine_us.model_api import *


class coverage_report_model_conflict(Variable):
    value_type = bool
    entity = Person
    label = "Marketplace coverage conflicts with modeled qualifying non-Marketplace coverage"
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("has_marketplace_health_coverage_at_interview", period) & person(
            "has_qualifying_non_marketplace_health_coverage_at_interview",
            period,
        )
