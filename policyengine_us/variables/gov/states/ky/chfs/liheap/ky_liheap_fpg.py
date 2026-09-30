from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ky_liheap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Kentucky LIHEAP annual federal poverty guideline"
    defined_for = StateCode.KY
    reference = "https://www.mkcap.org/uploads/3/4/8/3/34834615/2025-2026-liheap-fact-sheet-v2.jpg"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.chfs.liheap
        size = spm_unit("spm_unit_size", period)
        state_group = spm_unit.household("state_group_str", period)
        # The annual period represents the heating season ending in that year.
        # Only the guideline is lagged; household composition remains current.
        return fpg(
            max_(size, 1), state_group, period, parameters, year_lag=p.fpg_year_lag
        )
