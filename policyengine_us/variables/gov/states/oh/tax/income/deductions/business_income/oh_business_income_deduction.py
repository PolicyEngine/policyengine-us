from policyengine_us.model_api import *


class oh_business_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio business income deduction"
    documentation = "Ohio Schedule of Business Income, line 13."
    unit = USD
    definition_period = YEAR
    reference = (
        # R.C. 5747.01(A)(28)
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",
        "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2024/1040-bundle-original-fi.pdf#page=5",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.deductions.business_income
        # Line 11: the lesser of business income or federal adjusted gross
        # income, but not less than zero.
        business_income = tax_unit("oh_business_income", period)
        federal_agi = tax_unit("adjusted_gross_income", period)
        deductible = max_(min_(business_income, federal_agi), 0)
        # Lines 12-13
        filing_status = tax_unit("filing_status", period)
        return min_(deductible, p.cap[filing_status])
