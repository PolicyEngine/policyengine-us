from policyengine_us.model_api import *


class vt_aabd_ep_passes_state_resource_test(Variable):
    value_type = bool
    entity = Person
    label = "Vermont Essential Person state resource test passed"
    definition_period = MONTH
    defined_for = StateCode.VT
    default_value = False
    # PDF pages 46-48
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf#page=46"
    documentation = "Resource determination for state-only applicants under rule 2785, including Reach Up resource exclusions as of August 2024, Medicaid limits, and nonspouse dependent proration. SSI/AABD receipt by a household member of the group passes the resource test without this input."
