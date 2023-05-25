from policyengine_us.model_api import *


class nj_taxable_income_before_property_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey taxable income before property tax deduction"
    unit = USD
    documentation = "NJ AGI less taxable income deductions, before property tax deduction (Line 39)"
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3-1/"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        agi = tax_unit("nj_agi", period)
        deductions = tax_unit("nj_total_deductions", period)
        exemptions = tax_unit("nj_total_exemptions", period)
        return max_(0, agi - deductions - exemptions)
