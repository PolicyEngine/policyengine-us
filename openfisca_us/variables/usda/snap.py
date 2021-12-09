from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class is_disabled_or_elderly_for_snap(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates that a person is defined as disabled or elderly based on the USDA definition"
    label = "Is disabled or elderly for SNAP"


class snap_net_income_pre_shelter(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "SNAP net income before the shelter deduction, needed as intermediate to calculate shelter deduction"
    label = "SNAP net income (pre-shelter)"
    unit = "currency-USD"

    def formula(spm_unit, period):
        return max_(
            spm_unit("snap_gross_income", period)
            - spm_unit("snap_standard_deduction", period)
            - spm_unit("snap_earnings_deduction", period),
            0,
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


class snap_expected_contribution_towards_food(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Expected food contribution from SNAP net income"
    label = "SNAP expected food contribution"

    def formula(spm_unit, period, parameters):
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


class is_disabled_or_elderly_for_snap(Variable):

    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates that a person is defined as disabled or elderly based on the USDA definition"
