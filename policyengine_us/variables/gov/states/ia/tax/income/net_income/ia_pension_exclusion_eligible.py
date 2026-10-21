from policyengine_us.model_api import *


class ia_pension_exclusion_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Iowa pension exclusion"
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/media/2650/download?inline#page=27",
        "https://revenue.iowa.gov/media/2721/download?inline#page=26",
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.tax.income.pension_exclusion
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period)
        age_eligible = age >= p.minimum_age
        is_disabled = person("is_permanently_and_totally_disabled", period)
        return is_head_or_spouse & (age_eligible | is_disabled)
