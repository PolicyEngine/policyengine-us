from policyengine_us.model_api import *


class vt_ccfap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    defined_for = "vt_ccfap_eligible"
    label = "Vermont Child Care Financial Assistance Program benefit"
    reference = (
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=13",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=17",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/Act76/Memo-Act-76-CCFAP-Rule-Revision.pdf#page=11",
        "https://legislature.vermont.gov/statutes/section/33/035/03512",
    )
    # The state's payments to each child's provider. Together they come to the
    # children's rates less the family share, floored at zero.
    adds = ["vt_ccfap_child_payment"]
