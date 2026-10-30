from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class nv_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Nevada LIHEAP income limit"
    defined_for = StateCode.NV
    reference = (
        "https://www.leg.state.nv.us/nrs/nrs-702.html#NRS702Sec260",
        # PDF pages 43, 60, 110
        "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Energy/FY%202026%20EAP%20Manual%2008.2025%20ADA.pdf#page=43",
        # PDF pages 43, 60, 110
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/2027-eap-state-manual--08.25.26-1.pdf#page=43",
        "https://liheapch.acf.gov/docs/2026/state-plans/NV_Plan_2026.pdf#page=8",
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/fy-2027-low-income-home-energy-assistance-program-liheap-state-plan.pdf#page=8",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nv.dwss.liheap.eligibility
        size = spm_unit("nv_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        # Appendix A prints the annual limit unrounded (size 1: $23,475 in
        # SFY2026, $23,940 in SFY2027).
        return where(size > 0, guideline * p.fpg_rate, 0)
