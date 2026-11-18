from policyengine_us.model_api import *


class co_oap_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Colorado Old Age Pension countable income other than SSI"
    unit = USD
    definition_period = MONTH
    # PDF pages 76-78
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=76"
    # 9 CCR 2503-5 3.520.781(D)-(F): the client's own countable income
    # (3.533) plus income deemed from the spouse (3.534).
    adds = ["co_oap_own_countable_income", "co_oap_deemed_income"]
