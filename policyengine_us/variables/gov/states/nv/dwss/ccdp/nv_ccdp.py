from policyengine_us.model_api import *


class nv_ccdp(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Nevada CCDP benefit amount"
    definition_period = MONTH
    defined_for = "nv_ccdp_eligible"
    reference = "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Care/Child%20Care%20Manual%20July%202024.pdf#page=29"

    def formula(spm_unit, period, parameters):
        # MS 163: subsidy = min(provider charge, state maximum rate) - family
        # copay, paid up to 100% of the state maximum rate. The state maximum
        # rate is the per-day base rate converted to a monthly maximum using a
        # standard billed-days figure (Nevada does not publish an explicit
        # daily-to-monthly billing convention at the moment; a full-time-month
        # proxy is used, capped at actual childcare charges).
        # We don't track part-day/fractional-day rate adjustments or per-child
        # fee ordering at the moment.
        p = parameters(period).gov.states.nv.dwss.ccdp
        person = spm_unit.members
        daily_rate = person("nv_ccdp_provider_rate", period)
        monthly_max_rate = daily_rate * p.billing.monthly_billed_days
        # pre_subsidy_childcare_expenses is YEAR-defined; bare `period` in this
        # MONTH formula auto-divides it to a monthly amount.
        pre_subsidy_per_child = person("pre_subsidy_childcare_expenses", period)
        is_eligible_child = person("nv_ccdp_eligible_child", period)
        per_child_reimbursement = (
            min_(pre_subsidy_per_child, monthly_max_rate) * is_eligible_child
        )
        total_reimbursement = spm_unit.sum(per_child_reimbursement)
        copay = spm_unit("nv_ccdp_copay", period)
        return max_(total_reimbursement - copay, 0)
