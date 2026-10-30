from policyengine_us.model_api import *


class sc_tanf_need_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF need standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.SC
    # PDF pages 133-134
    reference = "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=133"  # Sections 8.15 and 8.16

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf.income.need_standard
        size = spm_unit("sc_tanf_benefit_group_size", period)
        # Section 8.15 sets the need standard as a share of the federal
        # poverty guideline for the number of persons in the benefit group,
        # revised each October 1, as in tanf_fpg.
        year = period.start.year
        if period.start.month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        p_fpg = parameters(instant_str).gov.hhs.fpg
        state_group = spm_unit.household("state_group_str", period.this_year)
        fpg = (
            p_fpg.first_person[state_group]
            + p_fpg.additional_person[state_group] * (size - 1)
        ) / MONTHS_IN_YEAR
        return where(size > 0, fpg * p.rate, 0)
