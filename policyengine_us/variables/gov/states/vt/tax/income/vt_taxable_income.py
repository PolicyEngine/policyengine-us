from policyengine_us.model_api import *


class vt_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont taxable income"
    unit = USD
    documentation = "VT AGI less taxable income deductions and exemptions"
    definition_period = YEAR
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf"
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        agi = tax_unit("vt_agi", period)
        deductions = tax_unit("vt_standard_deduction", period)
        exemptions = tax_unit("vt_personal_exemptions", period)
        return max_(0, agi - deductions - exemptions)
