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
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=13",
    )

    def formula(spm_unit, period, parameters):
        # The utility count and incurrence facts are YEAR-defined stocks
        # read at this MONTH period, so they are carried as is (no ÷12).
        distinct_utility_bills = spm_unit("count_distinct_utility_expenses", period)
        lua = parameters(period).gov.usda.snap.income.deductions.utility.limited
        region = spm_unit.household("snap_utility_region_str", period)
        always_sua = spm_unit("snap_state_using_standard_utility_allowance", period)
        has_heating_cooling = spm_unit("has_heating_cooling_expense", period)
        lua_is_defined = lua.active[region].astype(bool)
        # Under 7 CFR 273.9(d)(6)(iii)(A)(3), including telephone in the LUA
        # is a state option; where the state excludes it, a phone bill does
        # not count toward the two-utility LUA qualification.
        lua_includes_phone = lua.includes_phone[region].astype(bool)
        has_phone = spm_unit("has_phone_expense", period)
        lua_qualifying_bills = distinct_utility_bills - (
            has_phone & ~lua_includes_phone
        )
        # P.L. 119-21 section 10103 amends 7 U.S.C. 2014(e)(6)(C)(iv)(I) so
        # that receipt of energy assistance confers the SUA only on
        # households with an elderly or disabled member. In a state that
        # deems the SUA (always_sua), that route is what the deeming
        # models, so once the change is in effect the deemed SUA requires
        # an elderly or disabled member. An actual heating or cooling
        # expense still qualifies on its own, and always_standard itself is
        # unchanged: it records the state's option, not who may use it.
        #
        # California's SUAS test (ACL 25-68) has three parts: not otherwise
        # eligible for the SUA, not already receiving the maximum
        # allotment, and an elderly or disabled member. Only the third is
        # modelled, and it yields the same SNAP benefit as all three:
        #  - A household otherwise eligible for the SUA receives it anyway,
        #    through has_heating_cooling above.
        #  - "Already at the maximum allotment" is exactly
        #    snap_net_income == 0: net income is floored at zero and
        #    rounded, and the expected contribution is 30 percent of it
        #    rounded up, which is zero only when net income is zero. The
        #    utility allowance enters the shelter deduction only through
        #    max_(housing_cost - subtracted_income, 0) and min_(., cap), and
        #    the homeless branch takes the larger of the flat and regular
        #    deductions, so deductions never fall as the allowance rises.
        #    A household at the maximum without the SUA is therefore still
        #    at the maximum with it, and granting it changes no benefit.
        #    That comparison is between the SUA and whatever allowance the
        #    household would otherwise take. It holds in California because
        #    the SUA exceeds the LUA and every individual allowance there
        #    (663, 170 and at most 20 dollars in FFY 2026); a state where an
        #    individual allowance could exceed its SUA would need the leg
        #    modelled. The first two legs therefore decide who receives the
        #    SUAS payment, not the SNAP benefit, and are not modelled here.
        # This rests on the current deduction formula, not on a guarantee;
        # a change to how the allowance enters the deduction should revisit it.
        hr1 = spm_unit("is_snap_sua_hr1_in_effect", period)
        elderly_disabled = spm_unit("has_snap_elderly_disabled_member", period)
        deemed_sua = always_sua & (~hr1 | elderly_disabled)
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
