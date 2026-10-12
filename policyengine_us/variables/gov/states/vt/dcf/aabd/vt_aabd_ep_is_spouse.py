from policyengine_us.model_api import *


class vt_aabd_ep_is_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Vermont essential person is an ineligible spouse"
    definition_period = MONTH
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf"
