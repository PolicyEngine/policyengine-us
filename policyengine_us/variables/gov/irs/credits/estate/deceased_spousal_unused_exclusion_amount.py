from policyengine_us.model_api import *


class deceased_spousal_unused_exclusion_amount(Variable):
    value_type = float
    entity = Person
    label = "Deceased spousal unused exclusion amount"
    documentation = (
        "Deceased spousal unused exclusion (DSUE) amount that the estate of "
        "a surviving spouse can add to the basic exclusion amount under the "
        "portability election, as figured on Form 706 (Part 6, Section D). "
        "Enter the amount after the section 2010(c)(4) limits."
    )
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/2010#c_4",
        "https://www.irs.gov/pub/irs-prior/i706--2024.pdf#page=10",
    )
