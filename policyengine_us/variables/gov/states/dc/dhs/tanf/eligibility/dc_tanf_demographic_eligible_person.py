from policyengine_us.model_api import *


class dc_tanf_demographic_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible person for DC Temporary Assistance for Needy Families (TANF) based on demographics"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.18",
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.63",
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhs.tanf.age_threshold
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
