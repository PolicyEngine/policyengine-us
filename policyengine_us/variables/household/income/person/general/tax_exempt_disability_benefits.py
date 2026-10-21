from policyengine_us.model_api import *


class tax_exempt_disability_benefits(Variable):
    value_type = float
    entity = Person
    label = "tax-exempt disability benefits"
    unit = USD
    documentation = (
        "The part of disability_benefits excluded from gross income: benefits "
        "from a plan the recipient paid for with after-tax dollars, and the "
        "recipient's share of a plan both they and their employer paid for "
        "(IRC 104(a)(3), 105(a)). Premiums paid pre-tax through a cafeteria "
        "plan count as paid by the employer, so benefits they buy are taxable. "
        "Defaults to zero: benefits from employment are treated as coming from "
        "a plan the employer paid for."
    )
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.employment_income"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/104#a_3",
        "https://www.law.cornell.edu/uscode/text/26/105#a",
        "https://www.irs.gov/pub/irs-prior/p525--2024.pdf#page=18",
    )
