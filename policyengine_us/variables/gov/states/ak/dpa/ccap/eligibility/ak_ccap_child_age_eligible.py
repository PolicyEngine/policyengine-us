from policyengine_us.model_api import *


class ak_ccap_child_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Age eligible for Alaska CCAP"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = (
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=910",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=173",
    )

    def formula(person, period, parameters):
        # 7 AAC 41.060(a) caps the special-needs age limit at the same
        # under-13 threshold as the general child eligibility — Alaska does
        # not extend the federal CCDF special-needs age (up to 19) at the
        # moment. A single age check therefore covers both cases.
        p = parameters(period).gov.states.ak.dpa.ccap.age_threshold
        age = person("age", period.this_year)
        return age < p.child
