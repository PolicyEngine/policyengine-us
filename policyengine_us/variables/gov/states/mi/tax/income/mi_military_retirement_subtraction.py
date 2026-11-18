from policyengine_us.model_api import *


class mi_military_retirement_subtraction(Variable):
    value_type = float
    entity = Person
    label = "Michigan military retirement subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI
    reference = (
        "https://www.legislature.mi.gov/documents/mcl/pdf/mcl-206-30.pdf",  # (1)(e), (8)(c)
        "https://www.michigan.gov/taxes/questions/iit/accordion/military/are-military-survivor-retirement-benefits-that-pass-to-a-beneficiary",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2024/MI-1040-Instructions.pdf#page=13",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=12",
    )

    def formula(person, period, parameters):
        own_pay = person("military_retirement_pay", period)
        survivor_pay = person("military_retirement_pay_survivors", period)
        surviving_spouse = person("is_surviving_spouse", period)
        return own_pay + survivor_pay * surviving_spouse
