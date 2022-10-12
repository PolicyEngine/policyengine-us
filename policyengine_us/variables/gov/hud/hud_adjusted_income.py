from policyengine_us.model_api import *


class hud_adjusted_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD adjusted income"
    unit = USD
    documentation = "Adjusted income for HUD programs"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/5.611"

    def formula(spm_unit, period, parameters):
        # Extract annual income.
        income = spm_unit("hud_annual_income", period)
        # Count dependents - children only for now.
        child_count = aggr(spm_unit, period, ["is_child"])
        # Identify if elderly or disabled.
        elderly_disabled = spm_unit("is_hud_elderly_disabled_family", period)
        # Extract childcare expenses.
        # "Any reasonable child care expenses necessary to enable a member of
        # the family to be employed or to further his or her education."
        childcare_expenses = spm_unit("childcare_expenses", period)
        # TODO: Attendant care (save for later)
        # Medical expenses for elderly/disabled families.
        ded = parameters(period).gov.hud.adjusted_income.deductions
        moop = aggr(spm_unit, period, ["medical_out_of_pocket_expenses"])
        # Only expenses beyond a percent of income are deductible.
        moop_threshold = ded.moop.threshold * income
        moop_deductible = max_(0, moop - moop_threshold)
        moop_ded = moop_deductible * elderly_disabled
        # Add dependent and elderly disabled deductions.
        dependent_ded = ded.dependent.amount * child_count
        elderly_disabled_ded = ded.elderly_disabled.amount * elderly_disabled
        # Calculate and return adjusted income, non-negative.
        return max_(
            income
            - dependent_ded
            - elderly_disabled_ded
            - childcare_expenses
            - moop_ded,
            0,
        )
