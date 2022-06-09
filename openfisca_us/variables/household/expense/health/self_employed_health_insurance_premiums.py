from openfisca_us.model_api import *


class self_employed_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Self-employed health insurance premiums"
    unit = USD
    documentation = "Health insurance premiums for plans covering individuals who are not covered by any employer-sponsored health insurance."
    definition_period = YEAR

    def formula(person, period, parameters):
        is_self_employed = person("is_self_employed", period)
        health_insurance_premiums = person("health_insurance_premiums", period)
        return is_self_employed * health_insurance_premiums
