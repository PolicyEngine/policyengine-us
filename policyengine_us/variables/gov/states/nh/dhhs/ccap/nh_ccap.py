from policyengine_us.model_api import *


class nh_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "New Hampshire Child Care Scholarship Program benefit amount"
    definition_period = MONTH
    defined_for = "nh_ccap_eligible"
    reference = "https://www.law.cornell.edu/regulations/new-hampshire/N-H-Admin-Code-SS-He-C-6910.17"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        weeks_per_month = WEEKS_IN_YEAR / MONTHS_IN_YEAR

        weekly_rate = person("nh_ccap_payment_rate", period)
        disability_supplement = person("nh_ccap_disability_supplement", period)

        # Per-child pre-subsidy weekly expense
        annual_expense = person("pre_subsidy_childcare_expenses", period.this_year)
        weekly_expense = annual_expense / WEEKS_IN_YEAR

        # He-C 6910.17(e): payment = min(charge, WSR) - cost share
        capped_rate = min_(weekly_expense, weekly_rate)

        # He-C 6910.18(f): cost share divided equally among eligible children
        is_eligible_child = person("nh_ccap_eligible_child", period)
        n_eligible_children = add(spm_unit, period, ["nh_ccap_eligible_child"])
        family_cost_share = spm_unit("nh_ccap_cost_share", period)
        per_child_cost_share = np.zeros_like(family_cost_share)
        mask = n_eligible_children > 0
        per_child_cost_share[mask] = family_cost_share[mask] / n_eligible_children[mask]
        per_child_cost_share_broadcast = spm_unit.project(per_child_cost_share)

        # He-C 6910.17(g): disability supplement is additional, outside the min
        base_payment = max_(capped_rate - per_child_cost_share_broadcast, 0)
        per_child_weekly_payment = base_payment + disability_supplement
        per_child_monthly_payment = (
            per_child_weekly_payment * weeks_per_month * is_eligible_child
        )
        return spm_unit.sum(per_child_monthly_payment)
