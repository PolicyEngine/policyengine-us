from policyengine_us.model_api import *


class mn_claim_of_right_prior_year_tax_decrease(Variable):
    value_type = float
    entity = Person
    label = (
        "Minnesota prior-year tax decrease from excluding repaid claim of right income"
    )
    unit = USD
    documentation = (
        "Decrease in Minnesota income tax for the earlier year or years that "
        "would result solely from excluding the amount repaid this year "
        "(claim_of_right_repayment) from gross income for that year: the tax "
        "previously determined less that tax recomputed without the repaid "
        "income (Minn. R. 8007.0300, subpart 4). The tax unit uses the sum "
        "for its head and spouse."
    )
    definition_period = YEAR
    reference = (
        # Minn. Stat. 290.07, subdivision 4
        "https://www.revisor.mn.gov/statutes/cite/290.07",
        # Minn. R. 8007.0300
        "https://www.revisor.mn.gov/rules/8007.0300/",
        # 2025 Schedule M1REF, line 11
        "https://www.revenue.state.mn.us/sites/default/files/2025-12/m1ref-25.pdf#page=3",
    )
    defined_for = StateCode.MN
