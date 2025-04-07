from policyengine_us.model_api import *


class de_standard_deduction_joint(Variable):
    value_type = float
    entity = Person
    label = "Delaware standard deduction when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=8"
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        base_sd = person("de_base_standard_deduction_joint", period)
        add_sd = person("de_additional_standard_deduction", period)
        head = person("is_tax_unit_head", period)
        add_sd_attributed_to_head = person.tax_unit.sum(add_sd) * head
        return base_sd + add_sd_attributed_to_head
