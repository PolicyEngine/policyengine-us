from policyengine_us.model_api import *


class al_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AL
    documentation = (
        "Alabama other subtractions from Alabama gross income for adjustments reported on "
        "Form 40, Page 2, Part II, lines 1a-15 (total on line 16), that PolicyEngine does not compute, "
        "entered as a positive amount. Excludes lines 1a-1b (payments to an IRA), 2 (payments to a Keogh "
        "or SEP retirement plan), 3 (penalty on early withdrawal of savings), 4 (alimony paid), "
        "7 (health insurance deduction), 8 (Alabama CollegeCounts 529 and PACT contributions) and "
        "12 (contributions to a health savings account)."
    )
    # PDF pages 15-17
    reference = (
        "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/25f40bk.pdf#page=15"
    )
