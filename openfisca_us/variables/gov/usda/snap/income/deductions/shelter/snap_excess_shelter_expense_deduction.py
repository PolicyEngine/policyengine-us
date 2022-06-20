from openfisca_us.model_api import *


class snap_excess_shelter_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "Excess shelter expense deduction for calculating SNAP benefit amount"
    )
    label = "SNAP shelter deduction"
    reference = ("United States Code, Title 7, Section 2014(e)(6)",)
    unit = USD

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).usda.snap.income.deductions.excess_shelter_expense
        # Calculate uncapped shelter deduction as housing costs in excess of
        # income threshold.
        net_income_pre_shelter = spm_unit(
            "snap_net_income_pre_shelter", period
        )
        subtracted_income = p.income_share_disregard * net_income_pre_shelter
        housing_cost = spm_unit("housing_cost", period)
        uncapped_ded = max_(housing_cost - subtracted_income, 0)
        # Calculate capped deduction based on state group parameter.
        state_group = spm_unit.household("snap_region_str", period)
        ded_cap = p.cap[state_group] * MONTHS_IN_YEAR
        capped_ded = min_(uncapped_ded, ded_cap)
        has_elderly_disabled = spm_unit("has_usda_elderly_disabled", period)
        # Cap for all but elderly/disabled people and add utility allowance.
        non_homeless_shelter_deduction = where(
            has_elderly_disabled, uncapped_ded, capped_ded
        ) + spm_unit("snap_utility_allowance", period)
        # Homeless shelter deduction is flat and has no utility component.
        state = spm_unit.household("state_code_str", period)
        homeless_deduction = (
            p.homeless.deduction * MONTHS_IN_YEAR * p.homeless.available[state]
        )
        return where(
            spm_unit.household("is_homeless", period)
            & (housing_cost > 0)
            & (homeless_deduction > non_homeless_shelter_deduction),
            homeless_deduction,
            non_homeless_shelter_deduction,
        )
