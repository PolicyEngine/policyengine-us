from policyengine_us.model_api import *


class sc_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina CCAP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.SC
    reference = (
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=32",
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=33",
    )

    adds = "gov.states.sc.dss.ccap.income.countable_income.sources"
