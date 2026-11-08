from policyengine_us.model_api import *


class tax_exempt_strike_benefits(Variable):
    value_type = float
    entity = Person
    label = "tax-exempt strike benefits"
    unit = USD
    documentation = (
        "The part of strike_benefits excluded from gross income as a gift "
        "(IRC 102): benefits the facts clearly show the union meant as gifts "
        "(Pub. 525). Defaults to zero, because strike and lockout benefits "
        "are usually income."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/102#a",
        "https://www.irs.gov/pub/irs-prior/p525--2025.pdf#page=36",
        # Strike assistance found to be a gift on the facts.
        "https://www.govinfo.gov/content/pkg/USREPORTS-363/pdf/USREPORTS-363-299.pdf",
    )
