from policyengine_us.model_api import *


class wv_senior_citizen_disability_deduction_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the West Virginia senior citizen or disability deduction"
    definition_period = YEAR
    defined_for = StateCode.WV
    reference = "https://code.wvlegislature.gov/11-21-12/"

    def formula(person, period, parameters):
        wv_total_modifications = person(
            "wv_senior_citizen_disability_deduction_total_modifications",
            period,
        )
        wv_agi_person = person("wv_agi_person", period)

        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.senior_citizen_disability_deduction

        disabled_eligible = person("is_disabled", period)
        age = person("age", period)
        age_eligible = age >= p.age_threshold
        modification_eligible = (
            wv_total_modifications < p.total_modifications.limit
        )
        agi_eligible = wv_agi_person >= p.agi_limit

        return (
            (disabled_eligible | age_eligible)
            & modification_eligible
            & agi_eligible
        )
