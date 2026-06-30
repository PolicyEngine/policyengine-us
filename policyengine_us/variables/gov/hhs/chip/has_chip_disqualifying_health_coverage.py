from policyengine_us.model_api import *


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
        p = parameters(period).gov.hhs.chip
        return add(person, period, p.disqualifying_health_coverage) > 0
