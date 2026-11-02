from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class wv_lieap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "West Virginia LIEAP annual income limit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV
    reference = (
        # PDF pages 9,11
        "https://liheapch.acf.gov/docs/2026/state-plans/WV_Plan_2026.pdf#page=9",
        # FY2026 chart, PDF pages 406,1777
        "https://bfa.wv.gov/media/39948/download?inline=#page=406",
        # FY2027 chart, PDF pages 405,1779
        "https://bfa.wv.gov/media/40005/download?inline=#page=405",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("wv_lieap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        group = spm_unit.household("state_group_str", period)
        p = parameters(period).gov.states.wv.dhhr.lieap.eligibility
        annual_smi = liheap_smi_limit(size, state, p.smi_rate, period, parameters)
        annual_fpg = p.fpg_rate * fpg(
            size, group, period, parameters, year_lag=p.fpg_year_lag
        )
        annual = where(size <= p.smi_max_household_size, annual_smi, annual_fpg)
        # Nearest-dollar monthly rounding matches all ten published agency rows.
        # Apply the actual guideline to additional members, rather than repeatedly
        # adding a rounded increment; the latter diverges from the manual at 11.
        monthly = np.floor(annual / MONTHS_IN_YEAR + 0.5)
        return where(size > 0, monthly * MONTHS_IN_YEAR, 0)
