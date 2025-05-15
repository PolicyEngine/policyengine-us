from policyengine_us.model_api import *


class il_tanf_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible child for Illinois Temporary Assistance for Needy Families (TANF)"
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.30"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.tanf.age_threshold
        age = person("monthly_age", period)
        dependent = person("is_tax_unit_dependent", period)
        minor_child = age < p.minor_child
        eligible_minor_child = minor_child & dependent

        student_dependent = age <= p.student_dependent
        secondary_school_student = person("is_in_secondary_school", period)
        eligible_student_dependent = (
            secondary_school_student & student_dependent & dependent
        )
        immigration_status_eligible = person(
            "il_tanf_immigration_status_eligible_person", period
        )

        return immigration_status_eligible & (
            eligible_minor_child | eligible_student_dependent
        )
