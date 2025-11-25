from policyengine_us.model_api import *


class co_amt(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado alternative minimum tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
    reference = [
        "https://tax.colorado.gov/DR0104AMT",
        "https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-105/",
    ]

    def formula(tax_unit, period, parameters):
        tentative_minimum_tax = tax_unit("co_tentative_minimum_tax", period)
        # Normal tax before non-refundable credits
        normal_tax = tax_unit(
            "co_income_tax_before_non_refundable_credits", period
        )
        # AMT is the excess of tentative minimum tax over normal tax
        return max_(0, tentative_minimum_tax - normal_tax)
