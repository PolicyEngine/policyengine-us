from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ssa.state_supplement._and_cs_client_income import (
    and_cs_client_income,
)


class co_state_supplement_own_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Colorado State Supplement countable income of the client other than SSI"
    unit = USD
    definition_period = MONTH
    defined_for = "co_state_supplement_eligible"
    # PDF pages 93-94
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=93"

    def formula(person, period, parameters):
        # 9 CCR 2503-5 3.549(A) counts each AND-CS client's own income,
        # whether they are single, married or a member of an SSI couple.
        # The SSI that 3.549(A)(2)(d) adds back is added in co_state_supplement.
        p = parameters(period).gov.states.co.ssa.state_supplement.income.disregards
        earned, unearned, unearned_disregard, earned_disregard = and_cs_client_income(
            person, period, parameters
        )
        # 3.549(A)(1): deduct $65 from gross earned income and halve the rest.
        countable_earned = (
            max_(0, earned - p.earned - earned_disregard) * p.earned_share
        )
        return unearned - unearned_disregard + countable_earned
