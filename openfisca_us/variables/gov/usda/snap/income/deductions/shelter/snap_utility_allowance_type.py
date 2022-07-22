from openfisca_us.model_api import *


class SNAPUttilityAllowanceType(Enum):
    SUA = "Standard Utility Allowance"
    LUA = "Limited Utility Allowance"
    IUA = "Individual Utility Allowance"
    NONE = "None"


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
        distinct_utility_bills = spm_unit(
            "count_distinct_utility_expenses", period
        )
        lua = parameters(
            period
        ).gov.usda.snap.income.deductions.utility.limited
        region = spm_unit.household("snap_utility_region_str", period)
        lua_is_defined = lua.active[region].astype(bool)
        return select(
            [
                spm_unit("has_heating_cooling_expense", period),
                lua_is_defined & (distinct_utility_bills >= 2),
                distinct_utility_bills > 0,
                True,
            ],
            [
                SNAPUttilityAllowanceType.SUA,
                SNAPUttilityAllowanceType.LUA,
                SNAPUttilityAllowanceType.IUA,
                SNAPUttilityAllowanceType.NONE,
            ],
        )
