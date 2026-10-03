from policyengine_us.model_api import *


class hi_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii LIHEAP annual countable income"
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.HI
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/HI_Plan_2026.pdf#page=6,7",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.dhs.liheap.income
        # Annual flows approximate annualized prior-month income. All members'
        # income counts, including minor earnings and nonqualified members.
        # add() annualizes monthly SSI and adds household TANF only once.
        # Net business inputs require no second business-expense deduction.
        return max_(add(spm_unit, period, p.sources), 0)
