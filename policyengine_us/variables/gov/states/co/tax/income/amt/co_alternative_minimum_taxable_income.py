from policyengine_us.model_api import *


class co_alternative_minimum_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado alternative minimum taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
    reference = [
        "https://tax.colorado.gov/DR0104AMT",
        "https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-105/",
    ]

    def formula(tax_unit, period, parameters):
        # DR 0104AMT calculation:
        # Line 1: Federal Form 6251 line 6 (federal AMTI less exemption)
        federal_amt_income_less_exemptions = tax_unit(
            "amt_income_less_exemptions", period
        )
        # Line 2: Colorado additions (from DR 0104, lines 3-8)
        co_additions = tax_unit("co_additions", period)
        # Line 4: Colorado subtractions (excluding state income tax refund)
        co_subtractions = tax_unit("co_subtractions", period)
        # Line 5: Colorado AMTI
        return max_(
            0,
            federal_amt_income_less_exemptions
            + co_additions
            - co_subtractions,
        )
