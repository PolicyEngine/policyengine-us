from policyengine_us.model_api import *


class nd_military_retirement_subtraction(Variable):
    value_type = float
    entity = Person
    label = "North Dakota military retirement subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ND
    reference = (
        "https://ndlegis.gov/cencode/t57c38.pdf#page=35",  # 57-38-30.3(2)(r)
        "https://www.tax.nd.gov/military-service-members",
    )

    def formula(person, period, parameters):
        retirement_pay = person("military_retirement_pay", period)
        survivor_pay = person("military_retirement_pay_survivors", period)
        surviving_spouse = person("is_surviving_spouse", period)
        return retirement_pay + survivor_pay * surviving_spouse
