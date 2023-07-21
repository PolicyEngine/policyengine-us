from policyengine_us.model_api import *


class is_military(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Tax unit head is retired from United State military"
    unit = USD
    definition_period = YEAR
    documentation = "Delaware individual income tax instructions for 2022"
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=6"
