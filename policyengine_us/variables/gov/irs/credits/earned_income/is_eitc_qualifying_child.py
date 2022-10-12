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
        max_ages = parameters(
            period
        ).gov.irs.credits.eitc.qualifying_child.max_age
        max_age = where(student, max_ages.student, max_ages.non_student)
        age_qualifies = age <= max_age
        return dependent & (age_qualifies | disabled)
