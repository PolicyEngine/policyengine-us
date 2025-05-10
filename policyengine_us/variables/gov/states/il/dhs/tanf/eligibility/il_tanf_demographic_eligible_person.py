from policyengine_us.model_api import *


class il_tanf_demographic_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible person for Illinois Temporary Assistance for Needy Families (TANF) based on demographics"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.60",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.tanf.age_threshold
        age = person("monthly_age", period)
        dependent = person("is_tax_unit_dependent", period)
        minor_child = age < p.minor_child
        eligible_minor_child = minor_child & dependent

        student_dependent = age < p.student_dependent
        secondary_school_student = person("is_in_secondary_school", period)
        eligible_student_dependent = (
            secondary_school_student & student_dependent & dependent
        )

        pregnant = person("is_pregnant", period)
        return eligible_minor_child | eligible_student_dependent | pregnant
