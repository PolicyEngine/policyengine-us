from policyengine_us.model_api import *


class vt_aabd_ep_proration(Variable):
    value_type = float
    entity = Person
    label = "Vermont Essential Person certified payment fraction"
    definition_period = MONTH
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf"
    default_value = 1
    documentation = "Agency-certified fraction payable in the application month under rule 2784; a first-working-day application receives the full month."
