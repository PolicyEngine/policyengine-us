from policyengine_us.model_api import *


class co_ccap_num_child_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Number of children eligible for Colorado Child Care Assistance Program"
    definition_period = YEAR
    defined_for = StateCode.CO
    adds = ["co_ccap_child_eligible"]
