from policyengine_us.model_api import *


class ma_ccfa_is_nonparent_caregiver_family(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Massachusetts CCFA family with a nonparent caregiver and no resident parent"
    )
    documentation = "The child is in the care of a legal guardian, foster parent or other nonparent caregiver, with no parent living in the CCFA family."
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=76"
