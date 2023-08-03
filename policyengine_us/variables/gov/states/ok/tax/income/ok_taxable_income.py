from policyengine_us.model_api import *


class ok_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        agi = tax_unit("ok_agi", period)
        adjustments = tax_unit("ok_adjustments", period)
        std_ded = tax_unit("ok_standard_deduction", period)
        itm_ded = tax_unit("ok_itemized_deductions", period)
        deductions = where(itm_ded > std_ded, itm_ded, std_ded)
        exemptions = tax_unit("ok_exemptions", period)
        return max_(0, agi - adjustments - deductions - exemptions)
