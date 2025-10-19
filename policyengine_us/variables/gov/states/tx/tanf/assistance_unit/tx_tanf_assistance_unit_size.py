from policyengine_us.model_api import *


class tx_tanf_assistance_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Texas TANF assistance unit size"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-104",
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-220-tanf",
    )
    defined_for = StateCode.TX

    adds = [
        "tx_tanf_eligible_child",
        "tx_tanf_eligible_parent",
    ]
