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
        # Dependents per 24 CFR 5.603: under-18, disabled, or full-time
        # student members other than the head or spouse.
        dependent_count = add(spm_unit, period, ["is_hud_dependent"])
        # Identify if elderly or disabled.
        elderly_disabled = spm_unit("is_hud_elderly_disabled_family", period)
        # Extract childcare expenses.
        # "Any reasonable child care expenses necessary to enable a member of
        # the family to be employed or to further his or her education."
        # Per 24 CFR 5.611(a)(4), the deduction for employment-enabling
        # childcare cannot exceed the employment income included in annual
        # income.
        earned_income = spm_unit("hud_countable_earned_income", period)
        childcare_ded = min_(
            spm_unit("childcare_expenses", period), max_(earned_income, 0)
        )
        # Medical and disability assistance expenses per 24 CFR 5.611(a)(3):
        # the sum of unreimbursed medical expenses (elderly or disabled
        # families only) and attendant care expenses for disabled members
        # (any family), deductible to the extent the sum exceeds a share of
        # annual income. The attendant care portion cannot exceed the
        # employment income it enables (24 CFR 5.611(a)(3)(ii)).
        ded = parameters(period).gov.hud.adjusted_income.deductions
        moop = spm_unit("hud_medical_expenses", period)
        attendant_care = add(spm_unit, period, ["care_expenses"])
        capped_attendant_care = min_(attendant_care, max_(earned_income, 0))
        health_and_care_expenses = moop * elderly_disabled + capped_attendant_care
        moop_threshold = ded.moop.threshold * income
        moop_ded = max_(0, health_and_care_expenses - moop_threshold)
        # Add dependent and elderly disabled deductions.
        dependent_ded = ded.dependent.amount * dependent_count
        elderly_disabled_ded = ded.elderly_disabled.amount * elderly_disabled
        # Calculate and return adjusted income, non-negative.
        return max_(
            income - dependent_ded - elderly_disabled_ded - childcare_ded - moop_ded,
            0,
        )
