from policyengine_us.model_api import *


class vt_aabd(Variable):
    value_type = float
    entity = Person
    label = "Vermont Aid to the Aged, Blind or Disabled supplements"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.VT
    reference = (
        # 33 V.S.A. §§ 1301(3), 1309(a)
        "https://legislature.vermont.gov/statutes/fullchapter/33/013",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#m2",
        # PDF pages 27, 36
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf#page=27",
    )
    adds = ["vt_aabd_federal", "vt_aabd_ep"]
