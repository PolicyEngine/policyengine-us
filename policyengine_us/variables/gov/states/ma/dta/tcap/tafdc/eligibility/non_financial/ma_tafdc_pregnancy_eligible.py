from policyengine_us.model_api import *


class ma_tafdc_pregnancy_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) due to pregnancy"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-210"
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        is_pregnant = person("is_pregnant", period)
        age = person("age", period)
        current_pregnancy_month = person("current_pregnancy_month", period)
        p = parameters(period).gov.states.ma.dta.tcap.tafdc.eligibility
        age_limit = person("ma_tafdc_age_limit", period)
        age_eligible = age < age_limit
        # Eligible if pregnant and are in the 5th month or later (due in 120 days)
        months_eligible = is_pregnant & (
            current_pregnancy_month >= p.pregnancy_month
        )
        # Eligible if age under 20 and meet teen parent school attendance requirements
        is_in_secondary_school = person("is_in_secondary_school", period)
        teen_pregnancy_eligible = (
            is_pregnant & age_eligible & is_in_secondary_school
        )
        return teen_pregnancy_eligible | months_eligible
