from policyengine_us.model_api import *


class wv_senior_citizen_disability_deduction_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the West Virginia senior citizen or disability deduction"
    definition_period = YEAR
    defined_for = StateCode.WV
    reference = "https://code.wvlegislature.gov/11-21-12/"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.senior_citizen_disability_deduction

        disabled = person("is_permanently_and_totally_disabled", period)
        age = person("age", period)
        age_eligible = age >= p.age_threshold
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        return (disabled | age_eligible) & head_or_spouse
