from policyengine_us.model_api import *


class snap_work_requirement_disqualified(Variable):
    value_type = bool
    entity = Person
    label = "SNAP work requirement disqualified"
    documentation = "Person is disqualified from SNAP for failing work requirements under 273.7 (part of 273.11(c)(1) category)"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c_1"

    def formula(person, period, parameters):
        meets_work_req = person("meets_snap_work_requirements_person", period)
        is_ineligible_student = person("is_snap_ineligible_student", period)
        
        # Work requirement failures are distinct from student ineligibility
        # This identifies people subject to 273.11(c)(1) harsh treatment
        return ~meets_work_req & ~is_ineligible_student 