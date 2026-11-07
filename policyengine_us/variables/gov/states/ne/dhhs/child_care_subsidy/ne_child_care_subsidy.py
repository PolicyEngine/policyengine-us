from policyengine_us.model_api import *


class ne_child_care_subsidy(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Nebraska Child Care Subsidy"
    definition_period = MONTH
    reference = (
        "https://dhhs.ne.gov/Documents/CC-Subsidy-Provider-Booklet.pdf#page=28",
        "https://dhhs.ne.gov/Child%20Care%20Documents/ACF-118%20CCDF%20FFY%202025-2027%20For%20Nebraska%20-%20APPROVED.pdf#page=52",
        # PDF pages 3, 9-10, 21
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=3",
    )
    defined_for = "ne_child_care_subsidy_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy
        person = spm_unit.members
        # 392 NAC 1-001.04 and 2-004(E) limit child care to children within
        # the program's age limit, so the state pays nothing toward the bill
        # share of any other member, such as a teenager without a special need.
        eligible_child = person("ne_child_care_subsidy_eligible_child", period)
        private_charge = person("pre_subsidy_childcare_expenses", period)
        if not p.provider_rate_model_in_effect:
            # Preserve the prior expense-based approximation until the first
            # fully encoded provider-rate matrix takes effect.
            childcare_expenses = spm_unit.sum(private_charge * eligible_child)
            income = spm_unit("ne_child_care_subsidy_countable_income", period)
            fpg = spm_unit("spm_unit_fpg", period)
            fee_applies = income > fpg * p.fpg_fraction.fee_free_limit
            return where(
                fee_applies,
                max_(childcare_expenses - p.rate * income, 0),
                childcare_expenses,
            )
        # 392 NAC 2-004(H) and 3-001.02(C) also require an approved, enrolled
        # provider for each child the state pays for.
        covered = eligible_child & person(
            "ne_child_care_subsidy_provider_eligible", period
        )
        state_maximum = person("ne_child_care_subsidy_maximum_provider_rate", period)
        # When the rate matrix prices nothing for a covered child (the care
        # schedule is unreported, the general survey and microdata case),
        # the reimbursement falls back to that child's billed expenses.
        capped_charge = where(
            state_maximum > 0,
            min_(state_maximum, private_charge),
            private_charge,
        )
        reimbursement = spm_unit.sum(capped_charge * covered)
        family_fee = spm_unit("ne_child_care_subsidy_family_fee", period)
        return max_(reimbursement - family_fee, 0)
