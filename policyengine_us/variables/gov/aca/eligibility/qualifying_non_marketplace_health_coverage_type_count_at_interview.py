from policyengine_us.model_api import *


class qualifying_non_marketplace_health_coverage_type_count_at_interview(Variable):
    value_type = int
    entity = Person
    label = "Count of qualifying non-Marketplace health coverage types at interview"
    definition_period = YEAR
    adds = [
        "has_esi",
        "medicaid_enrolled",
        "has_medicaid_health_coverage_at_interview",
        "is_chip_eligible",
        "medicare_enrolled",
        "has_non_marketplace_direct_purchase_health_coverage_at_interview",
        "has_other_means_tested_health_coverage_at_interview",
        "has_tricare_health_coverage_at_interview",
        "has_champva_health_coverage_at_interview",
        "has_va_health_coverage_at_interview",
    ]
