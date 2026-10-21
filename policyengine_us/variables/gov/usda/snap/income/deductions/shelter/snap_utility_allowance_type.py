from policyengine_us.model_api import *


class SNAPUtilityAllowanceType(Enum):
    SUA = "Standard Utility Allowance"
    LUA = "Limited Utility Allowance"
    IUA = "Individual Utility Allowance"
    NONE = "None"


class snap_utility_allowance_type(Variable):
    value_type = Enum
    possible_values = SNAPUtilityAllowanceType
    entity = SPMUnit
    label = "SNAP utility allowance eligibility"
    default_value = SNAPUtilityAllowanceType.NONE
    documentation = "The type of utility allowance that is eligible for the SPM unit"
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-7/section-273.9#p-273.9(d)(6)(iii)(A)(3)",
        "https://www.law.cornell.edu/uscode/text/7/2014#e_6_C_iv_I",
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/html/PLAW-119publ21.htm",
    )

    def formula(spm_unit, period, parameters):
        # The utility count and incurrence facts are YEAR-defined stocks
        # read at this MONTH period, so they are carried as is (no ÷12).
        distinct_utility_bills = spm_unit("count_distinct_utility_expenses", period)
        p = parameters(period).gov.usda.snap.income.deductions.utility
        lua = p.limited
        region = spm_unit.household("snap_utility_region_str", period)
        always_sua = spm_unit("snap_state_using_standard_utility_allowance", period)
        has_heating_cooling = spm_unit("has_heating_cooling_expense", period)
        # P.L. 119-21 section 10103(a) restricts energy-assistance deeming,
        # while actual heating or cooling expenses still qualify on their own.
        deemed_sua = always_sua
        if p.heat_and_eat_requires_elderly_disabled:
            elderly_disabled = spm_unit("has_snap_elderly_disabled_member", period)
            deemed_sua = always_sua & elderly_disabled
        lua_is_defined = lua.active[region].astype(bool)
        # Under 7 CFR 273.9(d)(6)(iii)(A)(3), including telephone in the LUA
        # is a state option; where the state excludes it, a phone bill does
        # not count toward the two-utility LUA qualification.
        lua_includes_phone = lua.includes_phone[region].astype(bool)
        has_phone = spm_unit("has_phone_expense", period)
        lua_qualifying_bills = distinct_utility_bills - (
            has_phone & ~lua_includes_phone
        )
        return select(
            [
                has_heating_cooling | deemed_sua,
                lua_is_defined & (lua_qualifying_bills >= 2),
                distinct_utility_bills > 0,
            ],
            [
                SNAPUtilityAllowanceType.SUA,
                SNAPUtilityAllowanceType.LUA,
                SNAPUtilityAllowanceType.IUA,
            ],
            default=SNAPUtilityAllowanceType.NONE,
        )
