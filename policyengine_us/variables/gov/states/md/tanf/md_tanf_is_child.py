from policyengine_us.model_api import *

# reference: https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0300-Technical-Eligibility/0307%20Age%20rev%2011.22.doc


class md_tanf_is_child(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Is a child under Maryland TANF program"
    defined_for = StateCode.MD

    def formula(person, period, parameters):
        # younger than age 18
        child = person("is_child", period)
        # Younger than age 19 and A full time k12 student
        p = parameters(period).gov.states.md.tanf
        age_eligible = person("age", period) < p.age_limit
        k12 = person("is_in_k12_school", period)
        k12_age_eligible = k12 & age_eligible
        # age 19 and a full time student
        years_19 = person("age", period) == p.age_limit
        full_time_student = person("is_full_time_college_student", period)
        school_enrolled_19_year_old = full_time_student & years_19
        # return
        return child | school_enrolled_19_year_old | k12_age_eligible
