from policyengine_us.model_api import *


class health_savings_account_ald_person(Variable):
    value_type = float
    entity = Person
    label = "Health savings account ALD for each person"
    unit = USD
    documentation = (
        "This person's own health savings account deduction. A health savings "
        "account belongs to one individual, and each spouse with one figures "
        "the deduction on their own Form 8889. The tax unit's "
        "health_savings_account_ald remains the deduction its return claims; "
        "these amounts attribute it to the head and spouse where a state "
        "reports each spouse's adjustments separately. When they do not sum to "
        "it, it is shared in proportion to them, and when they are all zero, "
        "the head takes it."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/223#d_1",
        "https://www.irs.gov/pub/irs-pdf/i8889.pdf#page=2",
    )
