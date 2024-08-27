from policyengine_us.model_api import *

class nc_tanf_child_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Person-level eligiblity for TANF based on age and school status."

    def formula(person, period, parameters):
        child_0_17 = person("is_child", period)
        is_18 = person("age", period) == 18
        full_time_student = person("is_full_time_student", period)
        school_enrolled_18_year_old = full_time_student & is_18
        return child_0_17 | school_enrolled_18_year_old