from policyengine_us.model_api import *


class ok_tanf_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Oklahoma TANF"
    definition_period = YEAR
    reference = "https://oklahoma.gov/okdhs/library/policy/current/oac-340/chapter-10/subchapter-5/age.html"
    defined_for = StateCode.OK

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.tanf.eligibility
        age = person("age", period)
        is_student = person("is_full_time_student", period)

        # Per OAC 340:10-5-1: Through age 18, or through month turning 19 if student
        age_threshold = where(
            is_student,
            p.child_age_limit_student,
            p.child_age_limit,
        )
        return age < age_threshold
