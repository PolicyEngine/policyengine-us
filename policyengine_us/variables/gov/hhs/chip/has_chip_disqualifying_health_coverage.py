from policyengine_us.model_api import *


CHIP_DISQUALIFYING_HEALTH_COVERAGE_VARIABLES = [
    "has_esi",
    "medicaid_enrolled",
    "receives_medicaid",
    "has_medicaid_health_coverage_at_interview",
    "medicare_enrolled",
    "has_marketplace_health_coverage_at_interview",
    "has_non_marketplace_direct_purchase_health_coverage_at_interview",
    "has_other_means_tested_health_coverage_at_interview",
    "has_tricare_health_coverage_at_interview",
    "has_champva_health_coverage_at_interview",
    "has_va_health_coverage_at_interview",
]


class has_chip_disqualifying_health_coverage(Variable):
    value_type = bool
    entity = Person
    label = "Person has health coverage that disqualifies them from CHIP"
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-42/section-457.310#p-457.310(b)(2)",
        "https://www.ecfr.gov/current/title-42/section-457.320#p-457.320(b)(5)",
        "https://www.ecfr.gov/current/title-45/section-146.113#p-146.113(a)(1)",
    )

    def formula(person, period, parameters):
        return add(person, period, CHIP_DISQUALIFYING_HEALTH_COVERAGE_VARIABLES) > 0
