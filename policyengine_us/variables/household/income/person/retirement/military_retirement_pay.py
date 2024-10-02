from policyengine_us.model_api import *


class military_retirement_pay(Variable):
    value_type = float
    entity = Person
    label = "Military retirement pay"
    unit = USD
    definition_period = YEAR
    documentation = "The benefits received under a United States military retirement plan, including survivor benefits."
    reference = "https://militarypay.defense.gov/Pay/Retirement/"
