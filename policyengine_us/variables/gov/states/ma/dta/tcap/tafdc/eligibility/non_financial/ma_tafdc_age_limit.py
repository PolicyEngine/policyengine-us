from policyengine_us.model_api import *


class ma_tafdc_age_limit(Variable):
    value_type = float
    entity = Person
    label = "Applicable age limit for the Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-200"
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.tafdc.eligibility.age_limit
        is_in_secondary_school = person("is_in_secondary_school", period)
        # College attendees are not considered eligible dependents
        dependent_age_limit = where(
            is_in_secondary_school, p.student_dependent, p.dependent
        )
        is_pregnant = person("is_pregnant", period)
        teen_parent_age_limit = p.teen_parent
        return where(is_pregnant, teen_parent_age_limit, dependent_age_limit)
