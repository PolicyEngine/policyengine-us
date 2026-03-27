from policyengine_us.model_api import *


class has_age_exemption(Variable):
    value_type = bool
    entity = Person
    label = "Persons under 19 and 65 or older are exempt from Medicaid work requirements"
    definition_period = MONTH
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"

    def formula(person, period, parameters) -> bool:
        age = person("age", period)
        p = parameters(period).gov.hhs.medicaid.eligibility.work_requirements
        return p.age_range.calc(age)
