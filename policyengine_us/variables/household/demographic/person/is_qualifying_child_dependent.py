from policyengine_us.model_api import *


class is_qualifying_child_dependent(Variable):
    value_type = bool
    entity = Person
    label = "Is a qualifying child dependent based on age test"
    documentation = """
    A qualifying child must meet the age test under IRC 152(c)(3)(A):
    under 19 at end of year, or under 24 if a full-time student.
    This variable does NOT include the disability exception - that is
    handled separately in is_child_dependent.
    """
    reference = "https://www.law.cornell.edu/uscode/text/26/152#c_3_A"
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.irs.dependent.ineligible_age
        student = person("is_full_time_student", period)
        age_limit = where(student, p.student, p.non_student)
        return age < age_limit
