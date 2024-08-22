from policyengine_us.model_api import *


class is_person_demographic_tanf_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Person-level eligiblity for TANF based on age, pregnancy, etc."

    def formula(person, period, parameters):
        child_0_17 = person("is_child", period)
        is_18 = person("age", period) == 18
        full_time_student = person("is_full_time_student", period)
        school_enrolled_18_year_old = full_time_student & is_18
        pregnant = person("is_pregnant", period)
        return child_0_17 | school_enrolled_18_year_old | pregnant
