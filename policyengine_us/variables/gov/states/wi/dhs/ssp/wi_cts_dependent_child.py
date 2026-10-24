from policyengine_us.model_api import *


class wi_cts_dependent_child(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS dependent child"
    definition_period = MONTH
    # PDF pages 18, 21
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=18"
    documentation = "Requires a natural or adopted child. Set wi_cts_child_excluded for married or divorced minors or nonqualifying step/other relationships; annulled marriages do not exclude a minor."

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dhs.ssp.cts
        age = person("age", period.this_year)
        older_student = (
            (age < p.student_age_limit)
            & person("is_in_secondary_school", period.this_year)
            & person("wi_cts_graduates_before_19", period)
        )
        return ((age < p.minor_age_limit) | older_student) & ~person(
            "wi_cts_child_excluded", period
        )
