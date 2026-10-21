from policyengine_us.model_api import *


class oh_taxable_nonbusiness_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio taxable nonbusiness income"
    documentation = "Ohio IT 1040, line 7."
    unit = USD
    definition_period = YEAR
    reference = (
        # R.C. 5747.02(A)(3)
        "https://codes.ohio.gov/ohio-revised-code/section-5747.02",
        "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2024/1040-bundle-original-fi.pdf#page=1",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        # Line 5 minus line 6, not less than zero.
        income_tax_base = tax_unit("oh_taxable_income", period)
        taxable_business_income = tax_unit("oh_taxable_business_income", period)
        return max_(income_tax_base - taxable_business_income, 0)
