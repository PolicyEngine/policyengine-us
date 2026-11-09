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
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        # FY2026 federal amounts, PDF pages 3,6
        "https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM2025-02_SMIStateTable_Att4.pdf#page=3",
        # FY2027 federal amounts, PDF pages 3,6
        "https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_Att4SMITable_States_FY2027.pdf#page=3",
        # PDF pages 9,11
        "https://liheapch.acf.gov/docs/2026/state-plans/WV_Plan_2026.pdf#page=9",
        # PDF pages 9,12
        "https://bfa.wv.gov/media/39990/download?inline=#page=9",
        # FY2026 chart, PDF pages 407,1785
        "https://web.archive.org/web/20260302130424/https://bfa.wv.gov/media/39948/download?inline#page=407",
        # FY2027 chart, PDF pages 405,1779
        "https://web.archive.org/web/20261023203756/https://bfa.wv.gov/media/40005/download?inline#page=405",
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
        # Apply the actual guideline to additional members: the chart's rounded
        # add-on for each member above ten overshoots 150% of the guideline.
        monthly = np.floor(annual / MONTHS_IN_YEAR + 0.5)
        # 42 U.S.C. 8624(b)(2)(B) pays no household above the greater of 60% of SMI
        # and 150% of the guideline, which is annual at every size. A published
        # monthly amount that rounds up therefore stops there.
        limit = min_(monthly * MONTHS_IN_YEAR, annual)
        return where(size > 0, limit, 0)
