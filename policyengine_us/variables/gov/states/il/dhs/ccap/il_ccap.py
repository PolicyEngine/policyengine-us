from policyengine_us.model_api import *


class il_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Illinois CCAP ordinary child care subsidy"
    defined_for = "il_ccap_eligible"
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=54862",
        "https://www.dhs.state.il.us/page.aspx?item=10864",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap
        person = spm_unit.members
        eligible_child = person("il_ccap_eligible_child", period)
        provider_charge = person("pre_subsidy_childcare_expenses", period)
        maximum_reimbursement = person(
            "il_ccap_max_monthly_reimbursement",
            period,
        )
        reimbursable_cost = max_(
            min_(provider_charge, maximum_reimbursement),
            0,
        )
        total_reimbursable_cost = spm_unit.sum(reimbursable_cost * eligible_child)
        copay = spm_unit("il_ccap_copay", period)
        subsidy = max_(total_reimbursable_cost - copay, 0)
        return where(p.in_effect, subsidy, 0)
