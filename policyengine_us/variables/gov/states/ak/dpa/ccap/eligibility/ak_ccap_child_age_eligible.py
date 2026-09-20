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
        # This models PASS II/III under 7 AAC 41, with the under-13 limit
        # in 7 AAC 41.060(a) and manual 4070-2. Court status alone does not
        # extend this limit. PASS I (TANF, 7 AAC 45) and PASS IV protective
        # care are separate pathways, not established by this age test.
        p = parameters(period).gov.states.ak.dpa.ccap.age_threshold
        age = person("age", period.this_year)
        return age < p.child
