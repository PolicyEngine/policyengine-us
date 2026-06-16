from policyengine_us.model_api import *


class ms_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Mississippi child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=45"
    adds = ["ms_ccpp"]
