from policyengine_us.model_api import *


class ne_child_care_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nebraska Child Care Subsidy"
    definition_period = YEAR
    defined_for = "ne_child_care_subsidy_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy
        childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        income = add(spm_unit, period, ["adjusted_gross_income"])
        fpg = add(spm_unit, period, ["tax_unit_fpg"])
        fee_obligated = income > fpg * p.fpg_fraction_threshold
        capped_childcare_expenses_with_fee = max_(
            childcare_expenses - p.rate * income, 0
        )
        return where(
            fee_obligated,
            capped_childcare_expenses_with_fee,
            childcare_expenses,
        )
