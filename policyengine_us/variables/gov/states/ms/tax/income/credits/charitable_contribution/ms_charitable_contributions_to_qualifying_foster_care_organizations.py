from policyengine_us.model_api import *


class ms_charitable_contributions_to_qualifying_foster_care_organizations(Variable):
    value_type = float
    entity = TaxUnit
    label = "Charitable contributions to qualifying foster care organizations in Mississippi"
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100231.pdf#page=3"
