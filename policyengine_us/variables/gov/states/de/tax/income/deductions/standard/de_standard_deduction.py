from policyengine_us.model_api import *


class de_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware standard deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://delcode.delaware.gov/title30/c011/sc02/index.html title 30, chapter 11, subchapter II, section 1108"
    defined_for = StateCode.DE

    adds = ["de_base_standard_deduction", "de_additional_standard_deduction"]
