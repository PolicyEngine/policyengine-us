from policyengine_us.model_api import *


class co_state_supplement_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Colorado State Supplement countable income other than SSI"
    unit = USD
    definition_period = MONTH
    # PDF pages 93-96
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=93"
    # 9 CCR 2503-5 3.549(H): the client's own countable income plus income
    # deemed from the spouse or parents. Sponsor deeming (3.549(G)) and the
    # institutionalized spouse's MMMNA (3.549(F)) are not modeled.
    adds = [
        "co_state_supplement_own_countable_income",
        "co_state_supplement_deemed_income",
    ]
