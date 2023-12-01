from policyengine_us.model_api import *


class ky_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    reference = "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11"

    def formula(tax_unit, period, parameters):
        ky_agi = tax_unit("ky_agi", period)
        # current model does not have itemized deduction --> create a dummy one
        standard_deduction = tax_unit("ky_standard_deduction", period)
        itemized_deduction = tax_unit("ky_itemized_deduction", period)
        # if filler itemized deductions exceed standard deductions, it will benefit filler to itemize.
        deduction = where(itemized_deduction > standard_deduction, itemized_deduction, standard_deduction)

        return max_(0, ky_agi - deduction)
