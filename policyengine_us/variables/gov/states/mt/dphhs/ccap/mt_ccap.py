from policyengine_us.model_api import *


class mt_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Montana Best Beginnings Child Care Scholarship benefit amount"
    definition_period = MONTH
    defined_for = "mt_ccap_eligible"
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.202",
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.205",
    )

    def formula(spm_unit, period, parameters):
        # ARM 37.80.202/205: the department pays the lesser of the provider's
        # usual and customary charge or the state maximum rate for each eligible
        # child, minus the parent copayment. We don't track per-day attendance
        # at the moment, so full-month authorization is assumed (the 85%
        # attendance monthly-authorization rule and per-day billing are not
        # modeled).
        person = spm_unit.members
        is_eligible_child = person("mt_ccap_eligible_child", period)
        max_rate = person("mt_ccap_max_rate", period)
        pre_subsidy_expense = person("pre_subsidy_childcare_expenses", period)
        per_child_reimbursement = (
            min_(pre_subsidy_expense, max_rate) * is_eligible_child
        )
        total_reimbursement = spm_unit.sum(per_child_reimbursement)
        copay = spm_unit("mt_ccap_copay", period)
        return max_(total_reimbursement - copay, 0)
