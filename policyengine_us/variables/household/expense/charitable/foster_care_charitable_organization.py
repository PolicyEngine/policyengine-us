from policyengine_us.model_api import *


class foster_care_charitable_organization(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether a charitable organization is related to foster care"
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/arizona/2022/title-43/section-43-1088/"
    )
