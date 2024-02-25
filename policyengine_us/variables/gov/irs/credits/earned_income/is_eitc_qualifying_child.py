from policyengine_us.model_api import *


class is_eitc_qualifying_child(Variable):
    value_type = bool
    entity = Person
    label = "EITC qualifying child"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/152#c"

    def formula(person, period, parameters):
        dependent = person("is_tax_unit_dependent", period)
        disabled = person("is_permanently_and_totally_disabled", period)
        age = person("age", period)
        student = person("is_full_time_student", period)
        p = parameters(period).gov.irs.dependent.ineligible_age
        ineligible_age = where(student, p.student, p.non_student)
        age_qualifies = age < ineligible_age
        return dependent & (age_qualifies | disabled)
