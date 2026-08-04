from policyengine_us.model_api import *


class has_marketplace_health_coverage(Variable):
    value_type = bool
    entity = Person
    label = "Deprecated legacy Marketplace health coverage compatibility alias"
    definition_period = YEAR
    documentation = """
    Deprecated legacy Marketplace coverage status kept for compatibility.

    Use has_marketplace_health_coverage_at_interview for reported Marketplace
    coverage from survey data, and takes_up_aca_if_eligible for modeled ACA
    Marketplace take-up. ACA PTC eligibility and health benefit accounting do
    not depend on this variable.
    """

    def formula(person, period, parameters):
        return person("has_marketplace_health_coverage_at_interview", period)
