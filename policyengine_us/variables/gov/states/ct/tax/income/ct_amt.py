from policyengine_us.model_api import *


class ct_amt(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut alternative minimum tax (amt) rate"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/2022-CT-1040-Instructions_1222.pdf#page=22"  # line 9
        "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/CT-1040_1222.pdf#page=1"  # line 9
        "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/CT-6251_1222.pdf#page=1"  # line 23
    )

    def formula(tax_unit, period, parameters):
        # assign amt parameters
        p = parameters(period).gov.states.ia.tax.income
        amt = p.alternative_minimum_tax

        ct_taxable_income = tax_unit("ct_taxable_income", period)
        taxable_income = tax_unit("amt_income", period)
        federal_minimum_tax = tax_unit("alternative_minimum_tax", period)

        ct_minimum_tax = min_(
            taxable_income * amt.rate, federal_minimum_tax * amt.fraction
        )

        return max_(ct_minimum_tax - ct_taxable_income, 0)
