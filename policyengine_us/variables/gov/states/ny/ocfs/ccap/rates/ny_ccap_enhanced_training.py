from policyengine_us.model_api import *


class ny_ccap_enhanced_training(Variable):
    value_type = bool
    entity = Person
    label = "New York CCAP legally exempt group enhanced training requirement"
    definition_period = YEAR
    default_value = False
    defined_for = StateCode.NY
    documentation = (
        "Records whether the child's enrolled legally exempt group program "
        "meets the enhanced training requirement for the district's enhanced "
        "market rate, under 24-OCFS-LCM-22 and 18-OCFS-ADM-10. "
    )
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.9",
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=9",
    )
