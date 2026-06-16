from policyengine_us.model_api import *


class mo_ccs(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Missouri Child Care Subsidy benefit amount"
    definition_period = MONTH
    defined_for = "mo_ccs_eligible"
    reference = "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-060"

    def formula(spm_unit, period, parameters):
        # Reimbursement is paid per child at a daily rate for each day of care,
        # capped at the family's child care charges.
        person = spm_unit.members
        daily_benefit = person("mo_ccs_maximum_daily_benefit", period)
        days = person("childcare_attending_days_per_month", period.this_year)
        pre_subsidy_per_child = person("pre_subsidy_childcare_expenses", period)
        per_child_reimbursement = min_(daily_benefit * days, pre_subsidy_per_child)
        total_reimbursement = spm_unit.sum(per_child_reimbursement)
        copay = spm_unit("mo_ccs_copay", period)
        return max_(total_reimbursement - copay, 0)
