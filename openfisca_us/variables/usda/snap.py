from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *

# TODO: Add units where needed


class snap_minimum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Minimum benefit for SNAP"

    def formula(spm_unit, period, parameters):
        min_benefit = parameters(period).benefit.snap.minimum_benefit
        household_size = spm_unit.nb_persons()
        snap_max_benefits = parameters(period).usda.snap.amount.main
        state_group = spm_unit.household("state_group_str", period)
        relevant_max_benefit = snap_max_benefits[state_group][
            min_benefit.relevant_max_benefit_household_size
        ]
        min_share_of_max = where(
            household_size <= min_benefit.maximum_household_size,
            min_benefit.rate,
            0,
        )
        return relevant_max_benefit * min_share_of_max


class snap_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Gross income for calculating SNAP eligibility"
    label = "SNAP gross income"


class snap_earnings_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Earnings deduction for calculating SNAP benefit amount"
    label = "SNAP earnings deduction"

    def formula(spm_unit, period, parameters):

        snap_earnings_deduction = parameters(
            period
        ).usda.snap.earnings_deduction

        return spm_unit("snap_gross_income", period) * snap_earnings_deduction


class is_disabled_or_elderly_for_snap(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates that a person is defined as disabled or elderly based on the USDA definition"
    label = "Is disabled or elderly for SNAP"


class snap_standard_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Standard deduction for calculating SNAP benefit amount"
    label = "SNAP standard deduction"

    def formula(spm_unit, period, parameters):

        standard_deductions = parameters(period).usda.snap.standard_deduction

        state_group = spm_unit.household("state_group_str", period)
        # Households with more than 6 people have a 6-person households's
        # standard deduction.
        capped_household_size = min_(spm_unit.nb_persons(), 6)

        return standard_deductions[state_group][capped_household_size] * 12


class snap_net_income_pre_shelter(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Net income before shelter deduction, needed as intermediate to calculate shelter deduction"
    label = "SNAP net income pre-shelter"

    def formula(spm_unit, period, parameters):

        return (
            spm_unit("snap_gross_income", period)
            - spm_unit("snap_standard_deduction", period)
            - spm_unit("snap_earnings_deduction", period)
        )


class housing_cost(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing cost"
    unit = "currency-USD"
    definition_period = YEAR


class snap_shelter_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "Excess shelter deduction for calculating SNAP benefit amount"
    )
    label = "SNAP shelter deduction"

    def formula(spm_unit, period, parameters):
        # TODO: MUltiply params by 12.
        # check for member of spm_unit with disability/elderly status
        p_shelter_deduction = parameters(period).usda.snap.shelter_deduction

        # Calculate uncapped shelter deduction as housing costs in excess of
        # income threshold
        uncapped_ded = max_(
            spm_unit("housing_cost", period)
            - (
                p_shelter_deduction.income_share_threshold
                * spm_unit("snap_net_income_pre_shelter", period)
            ),
            0,
        )

        # Index maximum shelter deduction by state group.
        state_group = spm_unit.household("state_group_str", period)
        ded_cap = p_shelter_deduction.amount[state_group]

        has_elderly_disabled = spm_unit("has_elderly_disabled", period)
        # Cap for all but elderly/disabled people.
        return where(
            has_elderly_disabled, uncapped_ded, min_(uncapped_ded, ded_cap)
        )


class has_elderly_disabled(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Has elderly disabled"
    documentation = (
        "Whether elderly or disabled people, per USDA definitions, are present"
    )
    label = "Elderly or disabled person present"
    definition_period = YEAR


class snap_net_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Final net income, after all deductions"
    label = "SNAP net income"

    def formula(spm_unit, period, parameters):

        return spm_unit("snap_net_income_pre_shelter", period) - spm_unit(
            "snap_shelter_deduction", period
        )


class snap_expected_contribution_towards_food(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Expected food contribution from SNAP net income"
    label = "SNAP expected good contribution"

    def formula(spm_unit, period, parameters):
        # TODO: Use the parameter

        expected_food_contribution = parameters(
            period
        ).usda.snap.expected_food_contribution
        return spm_unit("snap_net_income", period) * expected_food_contribution


class snap_max_benefit(Variable):

    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Maximum benefit for SPM unit, based on the state group and household size."
    label = "SNAP maximum benefit"

    def formula(spm_unit, period, parameters):

        # TODO: Logic for families with >8 people
        snap_max_benefits = parameters(period).usda.snap.amount.main
        state_group = spm_unit.household("state_group_str", period)
        household_size = spm_unit.nb_persons()

        return snap_max_benefits[state_group][household_size] * 12


class snap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Final SNAP benefit amount, equal to net income minus food contribution"
    label = "SNAP benefit amount"

    def formula(spm_unit, period, parameters):
        # TODO: Add gross and net income checks.
        return max_(
            (
                spm_unit("snap_max_benefit", period)
                - spm_unit("snap_expected_contribution_towards_food", period)
            ),
            0 + snap_minimum_benefit,
        )


class is_disabled_or_elderly_for_snap(Variable):

    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates that a person is defined as disabled or elderly based on the USDA definition"


class snap_homeless_shelter_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Homeless shelter deduction"
    documentation = "Homeless shelter deduction"
    reference = "https://www.law.cornell.edu/cfr/text/7/273.9"

    def formula(spm_unit, period, parameters):

        is_homeless = spm_unit.household("is_homeless", period)
        return (
            is_homeless
            * parameters(period).usda.snap.homeless_shelter_deduction
        ) * 12
