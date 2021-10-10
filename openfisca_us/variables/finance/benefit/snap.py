from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.entity.spm_unit import *


class snap_earnings_deduction(Variable):
    value_type = int
    entity = spm_unit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        snap_earnings_deduction = parameters(
            period
        ).benefits.SNAP.earnings_deduction

        return spm_unit("gross_income") * snap_earnings_deduction


class snap_standard_deduction(Variable):
    value_type = int
    entity = spm_unit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        standard_deductions = parameters(
            period
        ).benefits.SNAP.standard_deduction

        state_group = spm_unit("state_group")

        household_size = spm_unit("household_size")

        return standard_deductions[state_group][household_size]


class snap_net_income_pre_shelter(Variable):
    value_type = int
    entity = spm_unit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        return (
            spm_unit("gross_income")
            - spm_unit("snap_standard_deduction")
            - spm_unit("snap_earnings_deduction")
        )


class snap_shelter_deduction(Variable):
    value_type = int
    entity = spm_unit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        # check for member of spm_unit with disability/elderly status

        p_shelter_deduction = parameters(
            period
        ).benefits.SNAP.shelter_deduction

        # Calculate uncapped shelter deduction as housing costs in excess of
        # income threshold
        uncapped_ded = max_(
            spm_unit("housing_cost")
            - (
                p_shelter_deduction.income_share_threshold
                * spm_unit("snap_net_income_pre_shelter")
            ),
            0,
        )

        # Index maximum shelter deduction by state group.
        state_group = spm_unit("state_group")
        ded_cap = p_shelter_deduction.amount[state_group]

        has_elderly_disabled = spm_unit("has_elderly_disabled")
        # Cap for all but elderly/disabled people.
        return where_(
            has_elderly_disabled, uncapped_ded, min_(uncapped, ded, ded_cap)
        )


class snap_net_income(Variable):
    value_type = int
    entity = spm_unit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        return spm_unit("snap_net_income_pre_shelter") - spm_unit(
            "snap_shelter_deduction"
        )


class snap_expected_contribution_towards_food(Variable):

    value_type = int
    entity = spm_unit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        return spm_unit("snap_net_income") * 0.3


class snap_max_benefit(Variable):

    value_type = int
    entity = spm_unit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        # we still need to figure out 8+ family member calcs
        SNAP_max_benefits = parameters(period).benefits.SNAP.amount.main

        state_group = spm_unit("state_group")

        household_size = spm_unit("household_size")

        return SNAP_max_benefits[household_size][state_group] * 12


class snap(Variable):

    value_type = int
    entity = spm_unit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        return spm_unit("snap_max_benefit") - spm_unit(
            "snap_expected_contribution_towards_food"
        )
