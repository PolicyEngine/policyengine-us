from policyengine_us.model_api import *


class ma_tafdc_eligible_dependent(Variable):
    value_type = bool
    entity = Person
    label = "Eligible dependent for the Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-200"
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.tafdc.eligibility.age_threshold
        dependent = person("is_tax_unit_dependent", period)
        
        # Basic age eligibility: under standard dependent age threshold
        standard_age_eligible = age < p.dependent
        
        # Special case for K-12 students: eligible if in school and under student dependent age
        # # College attendees are not considered eligible dependents
        in_school = person("is_in_k12_school", period)
        student_age_eligible = age < p.student_dependent
        school_eligible = in_school & student_age_eligible
        
        # Person must be a dependent and meet either age condition
        return dependent & (standard_age_eligible | school_eligible)
