from policyengine_us.model_api import *


class de_pension_exclusion_joint(Variable):
    value_type = float
    entity = Person
    label = "Delaware individual pension exclusion when married couples filing separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=6",
        "https://delcode.delaware.gov/title30/c011/sc02/index.html",
    )
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        head = person("is_tax_unit_head", period)
        pension_exclusions = add(
            person.tax_unit, period, ["de_pension_exclusion_indv"]
        )
        return head * pension_exclusions
