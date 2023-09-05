from policyengine_us.model_api import *


class az_charitable_contributions_to_qualifying_foster_care_organizations(
    Variable
):
    value_type = float
    entity = TaxUnit
    label = "Charitable contributions to qualifying foster care organizations in Arizona"
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = (
        "https://law.justia.com/codes/arizona/2022/title-43/section-43-1088/"
    )
