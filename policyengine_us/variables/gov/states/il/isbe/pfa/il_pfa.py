from policyengine_us.model_api import *


class il_pfa(Variable):
    value_type = float
    entity = Person
    label = "Illinois Preschool For All (PFA) benefit"
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.isbe.net/pages/preschool-for-all.aspx",
        "https://gov-pritzker-newsroom.prezly.com/gov-pritzker-announces-5150-new-preschool-seats-through-smart-start-initiative",
    )
    defined_for = "il_pfa_eligible"
    adds = ["gov.states.il.isbe.pfa.benefit.amount"]
