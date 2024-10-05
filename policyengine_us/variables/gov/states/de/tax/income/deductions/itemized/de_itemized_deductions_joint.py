from policyengine_us.model_api import *


class de_itemized_deductions_joint(Variable):
    value_type = float
    entity = Person
    label = "Delaware itemized deductions when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/TY22_PIT-RSA_2022-02_PaperInteractive.pdf",  # § 1109
        "https://delcode.delaware.gov/title30/c011/sc02/index.html",
    )
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        deductions = person.tax_unit("de_itemized_deductions_unit", period)
        is_head = person("is_tax_unit_head", period)
        return deductions * is_head
