from policyengine_us.model_api import *


class il_aabd_grant_amount(Variable):
    value_type = float
    entity = Person
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) grant amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=15948"

    adds = ["gov.states.il.dhs.aabd.payment.grant_amount"]
