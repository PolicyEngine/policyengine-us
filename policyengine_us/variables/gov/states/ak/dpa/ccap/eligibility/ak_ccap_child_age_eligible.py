from policyengine_us.model_api import *


class ak_ccap_child_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Age eligible for Alaska CCAP"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = (
        "https://www.akleg.gov/basis/aac.asp",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=173",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ak.dpa.ccap.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        return where(is_disabled, age < p.special_needs, age < p.child)
