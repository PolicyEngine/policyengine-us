from policyengine_us.model_api import *


class md_tanf_is_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Is a child under Maryland TANF program"
    defined_for = StateCode.MD
    reference = "https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0300-Technical-Eligibility/0307%20Age%20rev%2011.22.doc"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.tanf
        age = person("age", period.this_year)
        # Younger than age 18
        child = person("is_child", period.this_year)
        # Younger than age 19 and a full-time K-12 student
        age_eligible = age < p.age_limit
        k12 = person("is_in_k12_school", period)
        k12_age_eligible = k12 & age_eligible
        # Age 19 and a full-time student
        years_19 = age == p.age_limit
        full_time_student = person("is_full_time_college_student", period)
        school_enrolled_19_year_old = full_time_student & years_19
        return child | school_enrolled_19_year_old | k12_age_eligible
