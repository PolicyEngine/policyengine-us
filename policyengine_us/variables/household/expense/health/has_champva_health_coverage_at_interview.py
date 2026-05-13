from policyengine_us.model_api import *


class has_champva_health_coverage_at_interview(Variable):
    value_type = bool
    entity = Person
    label = "Person currently has CHAMPVA health coverage"
    definition_period = YEAR
