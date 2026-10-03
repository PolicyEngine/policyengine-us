from policyengine_us.model_api import *


class ar_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Arkansas LIHEAP countable income"
    defined_for = StateCode.AR
    reference = (
        # State plan sections 1.8-1.9, pages 5-7; application section III, page 2.
        "https://liheapch.acf.gov/docs/2026/state-plans/AR_Plan_2026.pdf#page=5",
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/fillable_aeo-9495_liheap-long-application.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ee.aeo.liheap.income
        person = spm_unit.members
        # Section III excludes minors' and full-time students' work income,
        # but requests non-work income from every household member.
        counted_worker = (
            person("age", period) >= p.minimum_earned_income_age
        ) & ~person("is_full_time_student", period)
        # Existing net business income approximates gross receipts. Additional
        # business/work-expense deductions and new gross inputs are deferred.
        earned_income = 0
        for source in p.sources.earned:
            earned_income = earned_income + max_(person(source, period), 0)
        countable_earnings = spm_unit.sum(earned_income * counted_worker) * (
            1 - p.earned_disregard
        )
        unearned_income = add(spm_unit, period, p.sources.unearned, options=[ADD])
        # Annual inputs approximate the application's preceding four weeks.
        # Otherwise countable income from every member is included in full,
        # even when that member is excluded from ar_liheap_household_size.
        return max_(countable_earnings + unearned_income, 0)
