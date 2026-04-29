from policyengine_us.model_api import *


class pa_ccw_stepparent_deduction(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Pennsylvania CCW stepparent deduction"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=76"

    def formula(spm_unit, period, parameters):
        has_stepparent = spm_unit("pa_ccw_has_stepparent", period)
        p = parameters(period).gov.states.pa.dhs.ccw.stepparent_deduction
        county_group = spm_unit.household(
            "pa_ccw_stepparent_county_group", period.this_year
        )
        size = spm_unit("spm_unit_size", period.this_year)
        # Appendix C starts at family size 2 because a stepparent deduction
        # only applies when there is at least one child in the assistance unit.
        capped_size = min_(max_(size, 2), p.max_family_size)
        extra = max_(size - p.max_family_size, 0)

        group_1_amount = p.group_1[capped_size] + extra * p.each_additional
        group_2_amount = p.group_2[capped_size] + extra * p.each_additional
        group_3_amount = p.group_3[capped_size] + extra * p.each_additional
        group_4_amount = p.group_4[capped_size] + extra * p.each_additional

        deduction = select(
            [
                county_group == 1,
                county_group == 2,
                county_group == 3,
                county_group == 4,
            ],
            [
                group_1_amount,
                group_2_amount,
                group_3_amount,
                group_4_amount,
            ],
        )
        return where(has_stepparent, deduction, 0)
