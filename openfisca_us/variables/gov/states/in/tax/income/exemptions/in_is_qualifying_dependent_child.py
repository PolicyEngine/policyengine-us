from openfisca_us.model_api import *


class in_is_qualifying_dependent_child(Variable):
    value_type = bool
    entity = Person
    label = "IN additional exemption qualifying dependent child"
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (5)(B)(i)

    def formula(person, period, parameters):
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        student = person("is_full_time_student", period)
        max_ages = (
            parameters(period)
            .gov.states["in"]
            .tax.income.exemptions.qualifying_child.max_ages
        )
        max_age = where(student, max_ages.student, max_ages.non_student)
        age_qualifies = age <= max_age
        return dependent & age_qualifies
