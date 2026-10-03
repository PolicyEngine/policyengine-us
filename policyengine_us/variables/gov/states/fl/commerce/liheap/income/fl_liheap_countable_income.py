from policyengine_us.model_api import *


class fl_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Florida LIHEAP annual countable household income"
    defined_for = StateCode.FL
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/FL_Plan_2026.pdf#page=5",
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/FL_PolicyManual_2023.pdf#page=49",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.commerce.liheap.income
        person = spm_unit.members
        age = person("age", period)
        adult = age >= p.adult_age
        # The current plan excludes all earnings under 18. The older detailed
        # manual supplies the unearned-income age rule where the current plan
        # is silent: include 16/17-year-olds who are not full-time students.
        unearned_age_eligible = adult | (
            (age >= p.nonstudent_min_age) & ~person("is_full_time_student", period)
        )
        # Preserve signed existing net business inputs without another expense
        # deduction. The sources do not specify a loss floor per business;
        # floor the combined household total. Rental income is nonnegative.
        earned = add(person, period, p.sources.earned)
        unearned = add(person, period, p.sources.unearned, options=[ADD])
        # Count the state cash grant once at SPM level as a caregiver grant.
        # Its calculated default is a receipt proxy; observed amounts can be
        # supplied through the existing variable. No national TANF aggregate.
        cash_grant = add(spm_unit, period, p.sources.household, options=[ADD])
        # Annual inputs approximate the prior 30 days/current economic situation.
        # Nonqualified members' countable income is retained in full. UI and
        # cash gifts are excluded by the current plan. Gross SSA is included;
        # the manual expressly adds Medicare premiums back to net checks.
        # Existing inputs do not isolate work-study, royalties, mortgage/sale
        # installments, and all countable insurance/lump-sum receipts.
        return max_(
            spm_unit.sum(earned * adult + unearned * unearned_age_eligible)
            + cash_grant,
            0,
        )
