from policyengine_us.model_api import *


class vt_aabd(Variable):
    value_type = float
    entity = Person
    label = "Vermont Aid to the Aged, Blind or Disabled supplements"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.VT
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#m",
        # PDF pages 27, 36
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf#page=27",
    )
    adds = ["vt_aabd_federal", "vt_aabd_ep"]
