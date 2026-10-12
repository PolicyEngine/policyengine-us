from policyengine_us.model_api import *


class estate_income(Variable):
    value_type = float
    entity = Person
    label = "Estate and trust income"
    unit = USD
    documentation = (
        "Net income or loss from an interest in an estate or trust reported on "
        "Schedule E Part III and carried to Schedule 1 line 5 (PUF E26390 less "
        "E26400). This covers Schedule K-1 (Form 1041) boxes 5 through 8; "
        "interest, dividends, and capital gains a beneficiary receives from an "
        "estate or trust belong in those separate inputs. Positive amounts "
        "enter federal gross income under IRC § 61(a)(14); losses are deducted "
        "through loss_ald."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/61#a_14",
        "https://www.irs.gov/pub/irs-prior/i1040se--2024.pdf#page=11",
        "https://www.irs.gov/pub/irs-prior/i1041sk1--2024.pdf#page=2",
    )
