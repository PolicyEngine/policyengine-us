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
    )
    defined_for = "ne_child_care_subsidy_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy
        if not p.provider_rate_model_in_effect:
            # Preserve the prior expense-based approximation until the first
            # fully encoded provider-rate matrix takes effect.
            childcare_expenses = spm_unit(
                "spm_unit_pre_subsidy_childcare_expenses", period
            )
            income = spm_unit("ne_child_care_subsidy_countable_income", period)
            fpg = spm_unit("spm_unit_fpg", period)
            fee_applies = income > fpg * p.fpg_fraction.fee_free_limit
            return where(
                fee_applies,
                max_(childcare_expenses - p.rate * income, 0),
                childcare_expenses,
            )
        person = spm_unit.members
        state_maximum = person("ne_child_care_subsidy_maximum_provider_rate", period)
        private_charge = person("pre_subsidy_childcare_expenses", period)
        # When the rate matrix prices nothing for a child (the care
        # schedule is unreported, the general survey and microdata case),
        # the reimbursement falls back to the billed childcare expenses.
        capped_charge = where(
            state_maximum > 0,
            min_(state_maximum, private_charge),
            private_charge,
        )
        reimbursement = spm_unit.sum(capped_charge)
        family_fee = spm_unit("ne_child_care_subsidy_family_fee", period)
        return max_(reimbursement - family_fee, 0)
