from policyengine_us.model_api import *


class capital_gains_28_percent_rate_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "28-percent rate gain"
    unit = USD
    documentation = "Includes collectibles and certain small business stock gains. These are taxed at a higher (28-percent) rate than other capital gains, while a proportion is excluded from taxable income."
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 1(h)(4)",
        href="https://www.law.cornell.edu/uscode/text/26/1#h_4",
    )

    adds = [
        "long_term_capital_gains_on_collectibles",
        "long_term_capital_gains_on_small_business_stock",
    ]
