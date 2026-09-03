from policyengine_us.model_api import *


class snap_limited_utility_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP Limited Utility Allowance"
    unit = USD
    documentation = "The limited utility allowance deduction for SNAP"
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-7/section-273.9#p-273.9(d)(6)(iii)(A)(3)"
    )

    def formula(spm_unit, period, parameters):
        utility = parameters(period).gov.usda.snap.income.deductions.utility
        p = utility.limited
        allowance_type = spm_unit("snap_utility_allowance_type", period)
        allowance_types = allowance_type.possible_values
        region = spm_unit.household("snap_utility_region_str", period)
        spm_size = spm_unit("spm_unit_size", period)
        MAX_SPM_SIZE = 10
        capped_size = max_(1, min_(MAX_SPM_SIZE, spm_size))
        lua_household_size_dependent = spm_unit(
            "snap_limited_utility_allowance_by_household_size", period
        )

        lua = where(lua_household_size_dependent, 0, p.main[region])

        # Under 7 CFR 273.9(d)(6)(iii)(A)(3), including telephone in the LUA
        # is a state option; where the state excludes it, the separate
        # telephone standard is added on top of the LUA for households with
        # phone costs.
        lua_includes_phone = p.includes_phone[region].astype(bool)
        has_phone = spm_unit("has_phone_expense", period)
        phone_standard = utility.single.phone[region]

        # change the state code to NC for the states that do not depend on household size to prevent key error
        region = where(lua_household_size_dependent, region, "NC")

        lua = where(
            lua_household_size_dependent,
            p.by_household_size.amount[region][capped_size],
            lua,
        )

        lua += ~lua_includes_phone * has_phone * phone_standard

        return where(allowance_type == allowance_types.LUA, lua, 0)
