from policyengine_us.model_api import *


class md_tanf_is_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Is a child under Maryland TCA program"
    defined_for = StateCode.MD
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.07.aspx"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.tanf
        age = person("age", period.this_year)
        # Younger than age 18
        child = person("is_child", period.this_year)
        # Younger than age 19 and a full-time K-12 student
        age_eligible = age < p.age_limit
        k12 = person("is_in_k12_school", period)
        k12_age_eligible = k12 & age_eligible
        # Age 19 and a full-time secondary school student
        # Per COMAR 07.03.03.07, extended eligibility is for secondary school
        # students only - college students do not qualify
        years_19 = age == p.age_limit
        secondary_school_enrolled_19_year_old = k12 & years_19
        return child | secondary_school_enrolled_19_year_old | k12_age_eligible
