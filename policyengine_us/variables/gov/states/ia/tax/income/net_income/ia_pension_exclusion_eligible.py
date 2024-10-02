from policyengine_us.model_api import *


class ia_pension_exclusion_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Iowa pension exclusion"
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=26"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=26"
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.tax.income.pension_exclusion
        # determine eligibility for pension exclusion
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # ... determine age eligibility
        age = person("age", period)
        age_eligible = age >= p.minimum_age
        head_or_spouse_age_eligible = is_head_or_spouse & age_eligible
        # ... determine disability eligiblity
        is_disabled = person("is_permanently_and_totally_disabled", period)
        is_disabled_head_or_spouse = is_head_or_spouse & is_disabled
        return age_eligible | is_disabled_head_or_spouse
