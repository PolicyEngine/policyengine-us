from policyengine_us.model_api import *


class is_snap_higher_ed_student(Variable):
    value_type = bool
    entity = Person
    label = "Is a higher education student for SNAP purposes"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/7/2015#e"

    def formula(person, period, parameters):
        # Students enrolled at least half-time in higher education
        # The statute covers half-time or more enrollment
        is_full_time_student = person("is_full_time_college_student", period)
        is_part_time_student = person("is_part_time_college_student", period)

        return is_full_time_student | is_part_time_student
