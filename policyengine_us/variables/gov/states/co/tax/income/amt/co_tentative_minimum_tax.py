from policyengine_us.model_api import *


class co_tentative_minimum_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado tentative minimum tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
    reference = [
        "https://tax.colorado.gov/DR0104AMT",
        "https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-105/",
    ]

    def formula(tax_unit, period, parameters):
        co_amti = tax_unit("co_alternative_minimum_taxable_income", period)
        p = parameters(period).gov.states.co.tax.income.amt
        # DR 0104AMT Line 6: multiply by 3.47%
        return co_amti * p.rate
