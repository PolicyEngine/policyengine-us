from policyengine_us.model_api import *


class ne_child_care_subsidy(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Nebraska Child Care Subsidy"
    definition_period = YEAR
    defined_for = "ne_child_care_subsidy_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy
        childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        income = spm_unit("spm_unit_net_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        fpg_fraction = fpg * p.fpg_fraction.fee_free_limit
        income_above_fpg_fraction = income > fpg_fraction
        capped_childcare_expenses_with_fee = max_(
            childcare_expenses - p.rate * income, 0
        )
        return where(
            income_above_fpg_fraction,
            capped_childcare_expenses_with_fee,
            childcare_expenses,
        )
