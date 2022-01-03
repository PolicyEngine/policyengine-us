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
    unit = "currency-USD"

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

        has_elderly_disabled = spm_unit("has_elderly_disabled", period)
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


class snap_net_income_pre_shelter(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "SNAP net income before the shelter deduction, needed as intermediate to calculate shelter deduction"
    label = "SNAP net income (pre-shelter)"
    unit = "currency-USD"
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_6_A"

    def formula(spm_unit, period):
        return max_(
            spm_unit("snap_gross_income", period)
            - spm_unit("snap_standard_deduction", period)
            - spm_unit("snap_earnings_deduction", period),
            0,
        )


class snap_homeless_shelter_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Homeless shelter deduction"
    documentation = "Homeless shelter deduction"
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.9#d_6_i",
        "United States Code, Title 7, Section 2014(e)(6)(D)",
    )
    unit = "currency-USD"

    def formula(spm_unit, period, parameters):
        is_homeless = spm_unit.household("is_homeless", period)
        return (
            is_homeless
            * parameters(period).usda.snap.homeless_shelter_deduction
        ) * 12


class SNAPUttilityAllowanceType(Enum):
    SUA = "Standard Utility Allowance"
    LUA = "Limited Utility Allowance"
    TUA = "Telephone Utility Allowance"
    NONE = "None"


class has_heating_cooling_expense(Variable):
    value_type = bool
    entity = Household
    label = "Has heating/cooling costs"
    documentation = "Whether the household has heating/cooling costs"
    definition_period = YEAR


class has_telephone_expense(Variable):
    value_type = bool
    entity = Household
    label = "Has telephone costs"
    documentation = "Whether the household has telephone (or equivalent) costs"
    definition_period = YEAR


class has_other_utility_expense(Variable):
    value_type = bool
    entity = Household
    label = "Has other utility expenses"
    documentation = "Whether the household has utility bills other than heating/cooling and telephone"
    definition_period = YEAR


class snap_utility_allowance_type(Variable):
    value_type = Enum
    possible_values = SNAPUttilityAllowanceType
    entity = SPMUnit
    label = "SNAP utility allowance eligibility"
    default_value = SNAPUttilityAllowanceType.NONE
    documentation = (
        "The type of utility allowance that is eligible for the SPM unit"
    )
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        return select(
            [
                spm_unit.household("has_heating_cooling_expense", period),
                spm_unit.household("has_other_utility_expense", period),
                spm_unit.household("has_telephone_expense", period),
                True,
            ],
            [
                SNAPUttilityAllowanceType.SUA,
                SNAPUttilityAllowanceType.LUA,
                SNAPUttilityAllowanceType.TUA,
                SNAPUttilityAllowanceType.NONE,
            ],
        )


class snap_utility_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Standard Utility Allowance"
    unit = "currency-USD"
    documentation = "The regular utility allowance deduction for SNAP"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        utility = parameters(period).usda.snap.deductions.utility
        allowance_type = spm_unit("snap_utility_allowance_type", period)
        state = spm_unit.household("state_code_str", period)
        return select(
            [
                allowance_type == SNAPUttilityAllowanceType.SUA,
                allowance_type == SNAPUttilityAllowanceType.LUA,
                allowance_type == SNAPUttilityAllowanceType.TUA,
                True,
            ],
            [utility.sua[state], utility.lua[state], utility.tua[state], 0],
        )
