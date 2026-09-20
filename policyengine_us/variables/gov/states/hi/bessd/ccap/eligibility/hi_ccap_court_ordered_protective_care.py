from policyengine_us.model_api import *


class hi_ccap_court_ordered_protective_care(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    defined_for = StateCode.HI
    label = "Hawaii CCAP court-ordered protective child care"
    reference = "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=14"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.hi.bessd.ccap.age
        age = person("age", period.this_year)
        protective = person("receives_or_needs_protective_services", period.this_year)
        ordered_care = person("requires_childcare_under_court_order", period.this_year)
        # Sections 17-798.2-2 and -9(a)(3): child under 18, receiving CPS,
        # with child care specified in the court-ordered family case plan.
        return protective & ordered_care & (age < p.protective_child_limit)
