from policyengine_us.model_api import *


class il_pfae(Variable):
    value_type = float
    entity = Person
    label = "Illinois Preschool For All Expansion (PFAE) benefit"
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.isbe.net/pages/preschool-for-all.aspx",
        "https://gov-pritzker-newsroom.prezly.com/gov-pritzker-announces-5150-new-preschool-seats-through-smart-start-initiative",
    )
    defined_for = "il_pfae_eligible"
    # PFA and PFAE share identical eligibility criteria. The difference is
    # service level: PFA provides half-day, PFAE provides full-day programs.
    # A child receives one or the other based on local program availability,
    # not both simultaneously.
    adds = ["gov.states.il.isbe.pfae.benefit.amount"]
