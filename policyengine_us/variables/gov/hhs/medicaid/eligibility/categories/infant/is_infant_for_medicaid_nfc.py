from policyengine_us.model_api import *


class is_infant_for_medicaid_nfc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid infant non-financial criteria"
    definition_period = YEAR

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.infant
        age = person("age", period)
        return ma.age_range.calc(age)
