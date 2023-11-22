from policyengine_us.model_api import *


class ri_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island taxable income"
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022_1040WE_w_0.pdf"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        ri_exemptions = tax_unit("ri_exemptions", period)
        # Modified Federal AGI
        mod_agi = tax_unit("ri_agi", period)
        ri_deductions = tax_unit("ri_standard_deduction", period)
        agi_less_deductions = max_(mod_agi - ri_deductions, 0)
        return max_(agi_less_deductions - ri_exemptions, 0)
