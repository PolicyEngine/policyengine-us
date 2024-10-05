from policyengine_us.model_api import *


class de_standard_deduction_indv(Variable):
    value_type = float
    entity = Person
    label = "Delaware standard deduction when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=8"
    defined_for = StateCode.DE

    adds = [
        "de_base_standard_deduction_indv",
        "de_additional_standard_deduction",
    ]
