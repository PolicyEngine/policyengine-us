from policyengine_us.model_api import *


class ky_liheap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Kentucky LIHEAP annual federal poverty guideline"
    defined_for = StateCode.KY
    reference = "https://www.mkcap.org/uploads/3/4/8/3/34834615/2025-2026-liheap-fact-sheet-v2.jpg"

    def formula_2026(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.chfs.liheap
        size = spm_unit("spm_unit_size", period)
        state_group = spm_unit.household("state_group_str", period)
        # Annual 2026 represents the heating season ending in 2026. Only the
        # guideline year is lagged; household composition remains current.
        fpg_year = period.start.year - int(p.fpg_year_lag)
        fpg = parameters(f"{fpg_year}-01-01").gov.hhs.fpg
        return fpg.first_person[state_group] + fpg.additional_person[
            state_group
        ] * max_(size - 1, 0)
