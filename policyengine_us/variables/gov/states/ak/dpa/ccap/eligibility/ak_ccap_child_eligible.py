from policyengine_us.model_api import *


class ak_ccap_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Alaska CCAP"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = (
        "https://www.akleg.gov/basis/aac.asp#7.41.350",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=173",
    )

    def formula(person, period, parameters):
        age_eligible = person("ak_ccap_child_age_eligible", period)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
