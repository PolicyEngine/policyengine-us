from policyengine_us.model_api import *


class has_other_means_tested_health_coverage_at_interview(Variable):
    value_type = bool
    entity = Person
    label = "Person currently has other means-tested health coverage"
    definition_period = YEAR
