from policyengine_us.model_api import *


class fl_sr_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida School Readiness countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = (
        "https://www.elcduval.org/wp-content/uploads/2025/07/Rule-6M-4.400_Frequently-Asked-Questions.pdf#page=1",
        "https://flrules.elaws.us/fac/6m-4.200",
    )

    # 6M-4.400 FAQ Q6: eligibility and copay use gross family income (no School
    # Readiness disregards).
    adds = "gov.states.fl.doe.sr.income.sources"
