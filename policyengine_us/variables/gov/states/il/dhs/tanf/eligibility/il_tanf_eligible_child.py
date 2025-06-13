from policyengine_us.model_api import *


class il_tanf_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible child for Illinois Temporary Assistance for Needy Families (TANF) based on demographics"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.60",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.tanf.age_threshold
        age = person("monthly_age", period)
        dependent = person("is_tax_unit_dependent", period)
        secondary_school_student = person("is_in_secondary_school", period)
        age_eligible = where(
            secondary_school_student,
            age <= p.student_dependent,
            age < p.minor_child,
        )

        return age_eligible & dependent
