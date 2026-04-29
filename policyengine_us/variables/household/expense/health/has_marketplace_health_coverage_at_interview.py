from policyengine_us.model_api import *


class has_marketplace_health_coverage_at_interview(Variable):
    value_type = bool
    entity = Person
    label = "Person currently has Marketplace health coverage"
    definition_period = YEAR
