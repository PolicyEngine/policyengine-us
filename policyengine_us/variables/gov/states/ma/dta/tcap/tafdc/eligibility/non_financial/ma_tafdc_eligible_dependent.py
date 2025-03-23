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
        dependent = person("is_tax_unit_dependent", period)

        # Basic age eligibility: under standard dependent age threshold
        age_limit = person("ma_tafdc_age_limit", period)
        age_eligible = age < age_limit

        # Person must be a dependent and meet either age condition
        return dependent & age_eligible
