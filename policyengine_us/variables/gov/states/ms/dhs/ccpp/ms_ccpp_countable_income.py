from policyengine_us.model_api import *


class ms_ccpp_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Mississippi CCPP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=29"

    adds = "gov.states.ms.dhs.ccpp.income.countable_income.sources"
