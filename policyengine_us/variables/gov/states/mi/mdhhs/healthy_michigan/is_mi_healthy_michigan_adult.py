from policyengine_us.model_api import *


class is_mi_healthy_michigan_adult(Variable):
    value_type = bool
    entity = Person
    label = "Michigan Healthy Michigan Plan adult"
    definition_period = YEAR
    defined_for = StateCode.MI
    reference = "https://dhhs.michigan.gov/olmweb/ex/BP/Mobile/BEM/BEM%20Mobile.pdf"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.categories.adult.age_range
        age = person("age", period)
        return p.calc(age)
