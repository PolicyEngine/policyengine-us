from policyengine_us.model_api import *


class state_benefit_cost(Variable):
    value_type = float
    entity = Person
    label = "State benefit cost attributed to this person"
    documentation = (
        "Sum of the state-government share of benefit expenditures for "
        "programs with statutory federal/state cost attribution (currently "
        "the state portion of Medicaid and CHIP). Distinct from "
        "`household_state_benefits`, which sums state-agency-paid "
        "standalone benefits like state supplements. The list of "
        "constituent variables lives at gov.household.state_benefit_cost "
        "so reforms can ablate programs."
    )
    unit = USD
    definition_period = YEAR
    adds = "gov.household.state_benefit_cost"
