from policyengine_us.model_api import *


class sd_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "South Dakota LIEAP annual countable household income"
    defined_for = StateCode.SD
    reference = (
        "https://sdlegislature.gov/Rules/Administrative/67:15:01:18",
        "https://sdlegislature.gov/Rules/Administrative/67:15:01:18.01",
        "https://liheapch.acf.gov/docs/2026/state-plans/SD_Plan_2026.pdf#page=6",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sd.dss.liheap.income
        person = spm_unit.members
        age = person("age", period)
        excluded_earnings = (age < p.earned_income_min_age) | (
            (age < p.secondary_school_age_limit)
            & person("is_in_secondary_school", period)
        )
        earned = 0
        for source in p.sources.earned:
            # Rule 67:15:01:18.01 counts self-employment losses as zero.
            # Use existing net sources without another business deduction.
            earned = earned + max_(person(source, period), 0)
        unearned = add(spm_unit, period, p.sources.unearned, options=[ADD])
        child_support_paid = add(spm_unit, period, ["child_support_expense"])
        # Rule 67:15:01:18(1) exempts earnings, not minor unearned income;
        # subsection (20) excludes income used to pay child support. State TANF
        # is counted once at SPM level; SSI and TANF are explicitly annualized.
        income = spm_unit.sum(earned * ~excluded_earnings) + unearned
        # This component supports fully qualified households. The manual refers
        # to an unavailable citizenship worksheet for allocating nonqualified
        # members' income; that mixed-status calculation is not implemented.
        # Annual inputs approximate stable income over the prior three months.
        # Medicare deductions are deferred. Existing inputs cannot isolate all
        # jury/foster receipts, program overpayment withholding, or expense refunds.
        return max_(income - child_support_paid, 0)
