from policyengine_us.model_api import *


class strike_benefits(Variable):
    value_type = float
    entity = Person
    label = "strike benefits"
    unit = USD
    documentation = (
        "Strike and lockout benefits a union pays, in cash or the fair market "
        "value of other property, including any part that is a gift. See "
        "taxable_strike_benefits and tax_exempt_strike_benefits."
    )
    definition_period = YEAR
    reference = ("https://www.irs.gov/pub/irs-prior/p525--2025.pdf#page=36",)
