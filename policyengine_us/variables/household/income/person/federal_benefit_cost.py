from policyengine_us.model_api import *


class federal_benefit_cost(Variable):
    value_type = float
    entity = Person
    label = "Federal benefit cost attributed to this person"
    documentation = (
        "Sum of the federal-government share of benefit expenditures for "
        "programs with statutory federal/state cost attribution (currently "
        "Medicaid per 42 U.S.C. 1396d(b)/(y) and CHIP per 42 U.S.C. "
        "1397ee(b)). The list of constituent variables lives at "
        "gov.household.federal_benefit_cost so reforms can ablate programs."
    )
    unit = USD
    definition_period = YEAR
    adds = "gov.household.federal_benefit_cost"
