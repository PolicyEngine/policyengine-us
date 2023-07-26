from policyengine_us.model_api import *


class ut_federal_deductions_for_taxpayer_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah federal deductions considered for taxpayer credit"
    unit = USD
    documentation = "These federal deductions are added to the Utah personal exemption to determine the Utah taxpayer credit."
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323"

    def formula(tax_unit, period, parameters):
        us_itemizing = tax_unit("tax_unit_itemizes", period)
        itm_ded_less_salt = tax_unit("itemized_deductions_less_salt", period)
        std_ded = tax_unit("standard_deduction", period)
        return where(us_itemizing, itm_ded_less_salt, std_ded)
