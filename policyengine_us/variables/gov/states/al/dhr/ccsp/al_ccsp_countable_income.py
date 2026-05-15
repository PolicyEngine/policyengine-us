from policyengine_us.model_api import *


class al_ccsp_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alabama CCSP countable monthly gross income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.AL
    reference = (
        "Alabama CCDF State Plan 2025-2027, Section 2.2.4(c)",
        "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=26",
    )

    adds = "gov.states.al.dhr.ccsp.income.countable_income.sources"
