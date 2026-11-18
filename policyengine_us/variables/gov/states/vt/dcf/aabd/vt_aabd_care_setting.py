from policyengine_us.model_api import *


class VTAABDCareSetting(Enum):
    RESIDENTIAL_CARE_LEVEL_III = (
        "Level III residential care home with assistive community care (code C)"
    )
    RESIDENTIAL_CARE_LEVEL_IV = (
        "Level IV residential care home or therapeutic community residence (code G)"
    )
    CUSTODIAL_CARE = "Custodial care family home (code H)"
    NONE = "No state-identified care setting"


class vt_aabd_care_setting(Variable):
    value_type = Enum
    entity = Person
    label = "Vermont AABD care setting"
    definition_period = MONTH
    defined_for = StateCode.VT
    possible_values = VTAABDCareSetting
    default_value = VTAABDCareSetting.NONE
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#m1",
        # PDF pages 31-33
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf#page=31",
    )
    documentation = "Residence in a care setting that meets the state's licensing, certification and service rules (rules 2764.1, 2764.3 and 2766)."
