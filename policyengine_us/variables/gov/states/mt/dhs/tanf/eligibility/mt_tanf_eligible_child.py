from policyengine_us.model_api import *


class mt_tanf_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible child for Montana TANF based on demographics"
    reference = "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.103#35"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.dhs.tanf.age_threshold
        age = person("monthly_age", period)
        dependent = person("is_tax_unit_dependent", period.this_year)
        secondary_school_student = person(
            "is_in_secondary_school", period.this_year
        )
        age_limit = where(
            secondary_school_student, p.student_dependent, p.minor_child
        )

        return dependent & (age < age_limit)
