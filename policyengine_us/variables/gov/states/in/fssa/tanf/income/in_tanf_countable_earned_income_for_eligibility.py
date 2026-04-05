from policyengine_us.model_api import *


class in_tanf_countable_earned_income_for_eligibility(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF countable earned income for eligibility determination"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://iar.iga.in.gov/code/2026/470/10.3#470-10.3-4-4",
        "https://iga.in.gov/laws/2025/ic/titles/12/#12-14-2-3",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        # NOTE: Uses calendar month as proxy for benefit duration.
        # Actual policy tracks cumulative months since enrollment.
        # All deductions ($90 work expense, $30 flat, 1/3 disregard)
        # are applied per earner per 470 IAC 10.3-4-4(c).
        p = parameters(period).gov.states["in"].fssa.tanf.income.deductions
        person = spm_unit.members
        gross_earned = person("tanf_gross_earned_income", period)

        # (c)(1): $90 per earner
        after_work_expense = max_(gross_earned - p.work_expense.amount, 0)

        is_enrolled = person.spm_unit("is_tanf_enrolled", period)
        month = period.start.month

        # (c)(2): $30 per earner (enrolled, months 1-12)
        after_flat = max_(after_work_expense - p.eligibility.flat_disregard.amount, 0)

        # (c)(3): 1/3 per earner (enrolled, months 1-4 only)
        in_one_third_phase = month <= p.eligibility.earned_income_disregard.months
        with_one_third = after_flat * (1 - p.eligibility.earned_income_disregard.rate)
        enrolled_countable = where(in_one_third_phase, with_one_third, after_flat)

        # Sum per-earner results to unit level
        return spm_unit.sum(where(is_enrolled, enrolled_countable, after_work_expense))
