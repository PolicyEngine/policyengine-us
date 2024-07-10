from policyengine_us.model_api import *


class md_snap_min_allotment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Maryland SNAP minimum allotment "
    defined_for = StateCode.MD
    reference = "https://casetext.com/statute/code-of-maryland/article-human-services/title-5-public-assistance/subtitle-5-food-stamps/section-5-501-food-supplement-program"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.usda.snap
        # Calculate the relevant maximum benefit, defined as the maximum
        # benefit for a household of a certain size in their state.
        snap_region = spm_unit.household("snap_region_str", period)
        relevant_max_allotment = p.max_allotment.main[snap_region][
            str(p.min_allotment.relevant_max_allotment_household_size)
        ]
        # Minimum benefits only apply to households up to a certain size.
        size = spm_unit("spm_unit_size", period)
        eligible = size <= p.min_allotment.maximum_household_size
        min_allotment = (
            eligible * p.min_allotment.rate * relevant_max_allotment
        )
        p_md = parameters(period).gov.states.md.snap.min_allotment
        md_min_allotment = p_md.amount
        person = spm_unit.members
        elderly = person("is_md_elderly", period)
        has_elderly = spm_unit.any(elderly)
        return where(
                has_elderly, md_min_allotment, min_allotment
            )