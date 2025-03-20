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
        ).gov.states.ma.dta.tafdc.eligibility.age_threshold
        # College attendees are not eligible dependents
        in_school = person("is_in_k12_school", period)
        student_age_eligible = age < p.child_under_19
        return age < p.child | (in_school & student_age_eligible)
