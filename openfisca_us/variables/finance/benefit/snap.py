from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.entity.household import *


class snap_earnings_deduction(Variable):
    value_type = int
    entity = household
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        snap_earnings_deduction = parameters(
            period
        ).benefits.SNAP.earnings_deduction

        return spm_unit(gross_income) * snap_earnings_deduction


class snap_standard_deduction(Variable):
    value_type = int
    entity = household
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
    entity = household
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        return (
            spm_unit(gross_income)
            - spm_unit(snap_standard_deduction)
            - spm_unit(snap_earnings_deduction)
        )


class snap_shelter_deduction(Variable):
    value_type = int
    entity = household
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        # check for member of household with disability/elderly status

        max_shelter_deductions = parameters(
            period
        ).benefits.SNAP.shelter_deduction

        if elderly_or_disabled == True:

            max_shelter_deductions = (
                max_shelter_deductions.elderly_or_disabled_exempt
            )

            return spm_unit(housing_cost) - (
                0.5 * spm_unit(snap_net_income_pre_shelter)
            )

        else:

            state_group = spm_unit("state_group")

            # note that the income used below must be SNAP net income - the other adjustments must come first

            if spm_unit(housing_cost) > (
                0.5 * spm_unit(snap_net_income_pre_shelter)
            ):

                return min(
                    (
                        (
                            spm_unit(housing_cost)
                            - (0.5 * spm_unit(snap_net_income_pre_shelter))
                        ),
                        max_shelter_deductions[state_group],
                    )
                )


class snap_net_income(Variable):
    value_type = int
    entity = household
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        return spm_unit(snap_net_income_pre_shelter) - spm_unit(
            snap_shelter_deduction
        )


class snap_expected_contribution_towards_food(Variable):

    value_type = int
    entity = household
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        return spm_unit(snap_net_income) * 0.3


class snap_monthly_benefit(Variable):

    value_type = int
    entity = household
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        SNAP_max_monthly_benefits = parameters(period).benefits.SNAP.amount

        state_group = spm_unit("state_group")

        household_size = spm_unit("household_size")

        return SNAP_max_monthly_benefits[household_size][
            state_group
        ] - spm_unit(snap_expected_contribution_towards_food)
