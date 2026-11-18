from policyengine_us.model_api import *


class vt_aabd_ep_nonspouse_essential_person(Variable):
    value_type = bool
    entity = Person
    label = "Vermont AABD recipient's certified Essential Person is not the spouse"
    definition_period = MONTH
    defined_for = StateCode.VT
    default_value = False
    # PDF pages 38, 40, 42
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf#page=38"
    documentation = "Set on the aged, blind or disabled recipient whose ineligible spouse lives with them but is not the certified essential person (rule 2781(E)); rule 2782 allows both in one assistance group."
