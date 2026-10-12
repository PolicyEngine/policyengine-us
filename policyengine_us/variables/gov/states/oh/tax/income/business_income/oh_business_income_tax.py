from policyengine_us.model_api import *


class oh_business_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio business income tax"
    documentation = (
        "Ohio Schedule of Business Income, line 16, and Ohio IT 1040, line 8b."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # R.C. 5747.02(A)(4)(a)
        "https://codes.ohio.gov/ohio-revised-code/section-5747.02",
        "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2024/1040-bundle-original-fi.pdf#page=5",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.business_income
        return tax_unit("oh_taxable_business_income", period) * p.rate
