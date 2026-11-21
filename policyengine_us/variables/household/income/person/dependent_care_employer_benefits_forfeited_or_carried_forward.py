from policyengine_us.model_api import *


class dependent_care_employer_benefits_forfeited_or_carried_forward(Variable):
    value_type = float
    entity = Person
    label = "Dependent care benefits forfeited or carried forward to the next year"
    documentation = (
        "Form 2441 line 14: the part of this person's "
        "dependent_care_employer_benefits (line 12) that they did not "
        "receive this year, either forfeited because no expense was incurred "
        "or carried forward to next year's grace period. On the 2021-2024 "
        "forms line 14 can also come from line 13. W-2 box 10 includes these "
        "amounts and box 1 leaves them out, as it leaves out all of line 12, "
        "so they are neither wages nor taxable dependent care benefits. Box "
        "10 amounts above the plan's exclusion are box 1 wages, not line 12, "
        "and do not go here. Enter each person's own amount: it reduces only "
        "that person's line 12 and line 13, and any amount beyond them counts "
        "as zero. In 2021 and 2022, when the federal calculation leaves line "
        "13 out, it subtracts all of this amount from line 12."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://www.irs.gov/pub/irs-prior/f2441--2025.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/i2441--2025.pdf#page=5",
        # Box 10 reports amounts "regardless of any employee forfeitures".
        "https://www.irs.gov/pub/irs-prior/iw2w3--2025.pdf#page=18",
        # Box 10 amounts "over your plan's exclusion" go in boxes 1, 3 and 5.
        "https://www.irs.gov/pub/irs-prior/iw2w3--2025.pdf#page=19",
    )
