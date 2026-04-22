from policyengine_us.model_api import *


class has_indian_health_service_coverage_at_interview(Variable):
    value_type = bool
    entity = Person
    label = "Person currently has Indian Health Service coverage"
    definition_period = YEAR
