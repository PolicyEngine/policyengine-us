from policyengine_us.model_api import *


class mt_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=1",
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=16",
    )

    def formula(tax_unit, period, parameters):
        mt_agi = tax_unit("mt_agi", period)
        standard_deduction = tax_unit("mt_standard_deduction", period)
        itemized_deductions = tax_unit("mt_itemized_deductions", period)
        # Tax units can claim the larger of the itemized or standard deductions
        deductions = max_(itemized_deductions, standard_deduction)
        exemptions = tax_unit("mt_exemptions", period)
        return max_(0, mt_agi - deductions - exemptions)
