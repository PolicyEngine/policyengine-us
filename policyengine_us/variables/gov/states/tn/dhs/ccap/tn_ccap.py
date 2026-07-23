from policyengine_us.model_api import *


class tn_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Tennessee CCAP benefit amount"
    definition_period = MONTH
    defined_for = "tn_ccap_eligible"
    reference = "https://www.tn.gov/content/dam/tn/human-services/documents/Reimbursement_Rate_Chart_1.1.26.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tn.dhs.ccap
        if not p.in_effect:
            return 0

        copay = spm_unit("tn_ccap_copay", period)
        max_weekly_benefit = add(spm_unit, period, ["tn_ccap_max_weekly_benefit"])
        max_monthly_benefit = max_weekly_benefit * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        # Reimbursement is the lesser of the provider charge and the state rate,
        # less the parent copay.
        capped_expenses = min_(pre_subsidy_childcare_expenses, max_monthly_benefit)
        return max_(capped_expenses - copay, 0)
