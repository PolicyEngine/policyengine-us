from policyengine_us.model_api import *


class oh_taxable_business_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio taxable business income"
    documentation = (
        "Ohio Schedule of Business Income, line 15, and Ohio IT 1040, line 6."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # R.C. 5747.02(A)(4)
        "https://codes.ohio.gov/ohio-revised-code/section-5747.02",
        "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2024/1040-bundle-original-fi.pdf#page=5",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        # Line 11
        business_income = tax_unit("oh_business_income", period)
        federal_agi = tax_unit("adjusted_gross_income", period)
        deductible = max_(min_(business_income, federal_agi), 0)
        # Line 14: business income above the deduction.
        deduction = tax_unit("oh_business_income_deduction", period)
        excess = deductible - deduction
        # Line 15: no more than the Ohio income tax base (IT 1040 line 5), so
        # exemptions that exceed nonbusiness income reduce taxable business
        # income (R.C. 5747.02(A)(4)(b)).
        income_tax_base = tax_unit("oh_taxable_income", period)
        return max_(min_(excess, income_tax_base), 0)
