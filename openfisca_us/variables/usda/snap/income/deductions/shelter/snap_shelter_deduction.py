from openfisca_us.model_api import *


class snap_shelter_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "Excess shelter deduction for calculating SNAP benefit amount"
    )
    label = "SNAP shelter deduction"
    reference = ("United States Code, Title 7, Section 2014(e)(6)",)
    unit = USD

    def formula(spm_unit, period, parameters):
        shelter_deduction = parameters(period).usda.snap.shelter_deduction

        # Calculate uncapped shelter deduction as housing costs in excess of
        # income threshold
        uncapped_ded = max_(
            spm_unit("housing_cost", period)
            - (
                shelter_deduction.income_share_threshold
                * spm_unit("snap_net_income_pre_shelter", period)
            ),
            0,
        )

        # Index maximum shelter deduction by state group.
        state_group = spm_unit.household("state_group_str", period)
        ded_cap = shelter_deduction.amount[state_group]

        has_elderly_disabled = spm_unit("has_usda_elderly_disabled", period)
        # Cap for all but elderly/disabled people.
        non_homeless_shelter_deduction = (
            where(
                has_elderly_disabled,
                uncapped_ded,
                12 * min_(uncapped_ded, ded_cap),
            )
            + spm_unit("snap_utility_allowance", period)
        )
        homeless_shelter_deduction = (
            spm_unit("snap_homeless_shelter_deduction", period)
        ) * 12
        return where(
            spm_unit.household("is_homeless", period),
            homeless_shelter_deduction,
            non_homeless_shelter_deduction,
        )
