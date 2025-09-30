from policyengine_us.model_api import *


class tx_tanf_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Texas Temporary Assistance for Needy Families (TANF) based on demographics"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-220-tanf",
        "https://www.law.cornell.edu/regulations/texas/1-TAC-372-307",
    )
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.tanf.age_threshold
        age = person("monthly_age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        is_secondary_school_student = person(
            "is_in_secondary_school", period.this_year
        )

        age_eligible = where(
            is_secondary_school_student,
            age < p.student_dependent,
            age < p.minor_child,
        )

        return age_eligible & is_dependent
