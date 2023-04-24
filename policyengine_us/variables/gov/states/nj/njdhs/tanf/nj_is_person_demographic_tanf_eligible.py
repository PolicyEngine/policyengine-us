from policyengine_us.model_api import *


class nj_is_person_demographic_tanf_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Person-level eligiblity for New Jersey TANF based on age."
    documentation = "Whether a person in a family applying for the Temporary Assistance for Needy Families program meets demographic requirements."

    def formula(person, period, parameters):
        child_under_18 = person("age", period) < 18
        is_under_19 = person("age", period) < 19
        full_time_student = person("is_full_time_student", period)
        school_enrolled_under_19_year_old = full_time_student & is_under_19
        return child_under_18 | school_enrolled_under_19_year_old
