from policyengine_us.model_api import *


class mi_ccap_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Currently enrolled in Michigan CDC"
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/703.pdf#page=17"
    )
