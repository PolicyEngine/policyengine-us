from policyengine_us.model_api import *


class hi_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii LIHEAP annual countable income"
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.HI
    reference = (
        # PDF pages 6-7
        "https://liheapch.acf.gov/docs/2026/state-plans/HI_Plan_2026.pdf#page=6",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.dhs.liheap.income
        # Annual flows approximate prior-month receipts. Minor and nonqualified
        # members' income counts; source losses cannot offset other receipts.
        person = spm_unit.members
        income = sum(max_(add(person, period, [source]), 0) for source in p.sources)
        return spm_unit.sum(income) + max_(spm_unit("tanf", period), 0)
