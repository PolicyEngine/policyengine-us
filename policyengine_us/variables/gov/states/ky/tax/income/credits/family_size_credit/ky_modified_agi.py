from policyengine_us.model_api import *


class ky_modified_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky modified adjusted gross income for the family size tax credit"
    unit = USD
    definition_period = YEAR
    reference = "file:///Users/pavelmakarchuk/Desktop/PolicyEngine/Tax%20Forms/Kentucky/740%20Packet%20Instructions%205-9-23.pdf#page=22"
    defined_for = StateCode.KY
