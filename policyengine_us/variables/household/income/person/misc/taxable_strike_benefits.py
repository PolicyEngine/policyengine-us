from policyengine_us.model_api import *


class taxable_strike_benefits(Variable):
    value_type = float
    entity = Person
    label = "taxable strike benefits"
    unit = USD
    documentation = (
        "Strike and lockout benefits other than gifts, which federal gross "
        "income includes under current law (Pub. 525); "
        "strike_benefits_in_gross_income follows the gross income sources "
        "under a reform. They are earned income (Pub. 596), reported on Form "
        "1040 line 1h from 2022."
    )
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-prior/p525--2025.pdf#page=36",
        "https://www.irs.gov/pub/irs-prior/p596--2025.pdf#page=8",
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=24",
    )

    def formula(person, period, parameters):
        strike_benefits = person("strike_benefits", period)
        # A gift part below zero is not a gift, so it never adds to the
        # benefits received.
        tax_exempt = max_(0, person("tax_exempt_strike_benefits", period))
        return max_(0, strike_benefits - tax_exempt)
