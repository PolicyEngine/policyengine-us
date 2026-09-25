from policyengine_us.model_api import *


class snap_max_allotment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "Maximum SNAP allotment for SPM unit, based on the state group and household size."
    label = "SNAP maximum allotment"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/7/2012#u_2"

    def formula(spm_unit, period, parameters):
        max_allotments = parameters(period).gov.usda.snap.max_allotment
        MAX_HOUSEHOLD_SIZE_UNDER_MAIN = 8
        snap_region = spm_unit.household("snap_region_str", period)
        household_size = min_(
            spm_unit("snap_unit_size", period), MAX_HOUSEHOLD_SIZE_UNDER_MAIN
        )
        additional_members = max_(
            0,
            spm_unit("snap_unit_size", period) - MAX_HOUSEHOLD_SIZE_UNDER_MAIN,
        )
        main_allotment = max_allotments.main[snap_region][household_size]
        additional_allotment = (
            additional_members * max_allotments.additional[snap_region]
        )
        return main_allotment + additional_allotment

    def formula_2026_10_01(spm_unit, period, parameters):
        allotment = snap_max_allotment.formula(spm_unit, period, parameters)
        snap_region = spm_unit.household("snap_region_str", period)
        # 7 U.S.C. 2012(u)(2)(I), as amended by P.L. 119-21, limits the
        # increment for households of 9 or more to 200 percent of the
        # four-person allotment. USDA's FY2026 table listed only a
        # per-person increment; its FY2027 memo first published the
        # resulting 18+ caps, so the cap applies from October 2026.
        cap = parameters(period).gov.usda.snap.max_allotment.cap[snap_region]
        return min_(allotment, cap)
