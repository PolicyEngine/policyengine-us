from policyengine_us.model_api import *


class ut_state_tax_refund(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah state tax refund"
    unit = USD
    documentation = "Form TC-40, line 7"
    definition_period = YEAR
    defined_for = StateCode.UT

    adds = ["salt_refund_last_year"]
