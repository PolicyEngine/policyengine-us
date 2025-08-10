from policyengine_us.model_api import *


class il_aabd_is_bedfast(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Whether the person is a bedfast client under the Illinois Aid to the Aged, Blind or Disabled (AABD)"
    reference = "https://www.dhs.state.il.us/page.aspx?item=15913"
    defined_for = StateCode.IL
