from policyengine_us.model_api import *


class dc_pap_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible child for DC Public Assistance Programs based on demographics"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.18"
    )
    defined_for = "dc_tanf_immigration_status_eligible_person"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhs.tanf.age_threshold
        age = person("monthly_age", period)
        dependent = person("is_tax_unit_dependent", period)
        secondary_school_student = person("is_in_secondary_school", period)
        age_limit = where(
            secondary_school_student, p.student_dependent, p.minor_child
        )

        return dependent & (age < age_limit)
