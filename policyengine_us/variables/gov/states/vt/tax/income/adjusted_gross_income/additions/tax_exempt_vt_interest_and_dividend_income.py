from policyengine_us.model_api import *


class tax_exempt_vt_interest_and_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "Vermont tax-exempt interest and dividened income"
    definition_period = YEAR
    defined_for = StateCode.VT
    documentation = "Interest and dividend income from Vermont state and local obligations exempted from federal tax."
