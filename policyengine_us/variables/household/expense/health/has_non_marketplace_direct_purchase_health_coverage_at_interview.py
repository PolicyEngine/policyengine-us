from policyengine_us.model_api import *


class has_non_marketplace_direct_purchase_health_coverage_at_interview(Variable):
    value_type = bool
    entity = Person
    label = "Person currently has non-Marketplace direct-purchase health coverage"
    definition_period = YEAR
