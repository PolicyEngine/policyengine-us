from policyengine_us.model_api import *


class in_tanf_countable_earned_income_for_eligibility(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "Indiana TANF countable earned income for eligibility determination"
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://iar.iga.in.gov/code/2026/470/10.3#470-10.3-4-4",
        "https://iga.in.gov/laws/2025/ic/titles/12/#12-14-2-3",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        # NOTE: The $30 and 1/3 disregard only applies for the first 4 months
        # of continuing eligibility. This simplified implementation always
        # applies the $30 and 1/3 disregard.
        p = parameters(period).gov.states["in"].fssa.tanf.income.deductions
        person = spm_unit.members
        gross_earned = person("tanf_gross_earned_income", period)

        # $90 per earner, then $30 + 1/3 per unit (470 IAC 10.3-4-4(c))
        after_work_expense = spm_unit.sum(
            max_(gross_earned - p.work_expense.amount, 0)
        )
        after_flat = max_(
            after_work_expense - p.eligibility.flat_disregard.amount, 0
        )
        return after_flat * (1 - p.eligibility.earned_income_disregard.rate)
