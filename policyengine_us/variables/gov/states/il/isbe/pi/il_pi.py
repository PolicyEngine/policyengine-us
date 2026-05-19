from policyengine_us.model_api import *


class il_pi(Variable):
    value_type = float
    entity = Person
    label = "Illinois Prevention Initiative (PI) benefit"
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.isbe.net/Pages/Birth-to-Age-3-Years.aspx",
        "https://gov-pritzker-newsroom.prezly.com/gov-pritzker-announces-5150-new-preschool-seats-through-smart-start-initiative",
    )
    defined_for = "il_pi_eligible"
    adds = ["gov.states.il.isbe.pi.benefit.amount"]
