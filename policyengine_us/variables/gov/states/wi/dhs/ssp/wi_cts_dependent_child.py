from policyengine_us.model_api import *


class wi_cts_dependent_child(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS dependent child"
    definition_period = MONTH
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
    documentation = "Requires a natural or adopted child. Override or set child_excluded for divorced minors or nonqualifying step/other relationships; annulled marriages do not exclude a minor."

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dhs.ssp.cts
        age = person("age", period.this_year)
        older_student = (
            (age < p.student_age_limit)
            & person("is_in_secondary_school", period.this_year)
            & person("wi_cts_graduates_before_19", period)
        )
        return (
            ((age < p.minor_age_limit) | older_student)
            & (person.marital_unit.nb_persons() == 1)
            & ~person("wi_cts_child_excluded", period)
        )
