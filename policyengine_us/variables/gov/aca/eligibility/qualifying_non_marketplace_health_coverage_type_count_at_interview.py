from policyengine_us.model_api import *


class qualifying_non_marketplace_health_coverage_type_count_at_interview(Variable):
    value_type = int
    entity = Person
    label = "Count of qualifying non-Marketplace health coverage types at interview"
    definition_period = YEAR
    adds = "gov.aca.qualifying_non_marketplace_health_coverage"
