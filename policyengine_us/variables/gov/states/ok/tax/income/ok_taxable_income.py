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
        exemptions = tax_unit("ok_exemptions", period)
        # From page 10 of the 2021 and 2022 Form 511 Packets:
        #   "If you claimed the standard deduction on your federal return,
        #   you must claim the Oklahoma standard deduction. If you claimed
        #   itemized deductions on your federal return, you must claim
        #   Oklahoma itemized deductions."
        std_ded = tax_unit("ok_standard_deduction", period)
        itm_ded = tax_unit("ok_itemized_deductions", period)
        federal_itemizer = tax_unit("tax_unit_itemizes", period)
        deductions = where(federal_itemizer, itm_ded, std_ded)
        return max_(0, agi - adjustments - exemptions - deductions)
