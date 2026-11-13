from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


def al_liheap_income_limit_for_lag(spm_unit, period, parameters, year_lag):
    p = parameters(period).gov.states.al.adeca.liheap.eligibility
    p_hhs = parameters(period).gov.hhs.liheap
    size = spm_unit("al_liheap_household_size", period)
    state = spm_unit.household("state_code_str", period)
    state_group = spm_unit.household("state_group_str", period)
    guideline = fpg(
        max_(size, 1),
        state_group,
        period,
        parameters,
        year_lag=year_lag,
    )
    monthly_limit = guideline * p.fpg_rate / MONTHS_IN_YEAR
    # Nearest-dollar, half-up rounding reproduces all 15 printed limits.
    rounded_limit = np.floor(monthly_limit + 0.5) * MONTHS_IN_YEAR
    # 42 U.S.C. 8624(b)(2)(B) pays no household above the greater of 150% of the
    # poverty guideline and 60% of state median income, in the amounts HHS
    # publishes by household size. A published monthly amount that rounds above
    # that maximum stops there.
    smi_maximum = liheap_smi_limit(size, state, p_hhs.smi_limit, period, parameters)
    return min_(rounded_limit, max_(guideline * p_hhs.fpg_limit, smi_maximum))


class al_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alabama LIHEAP annualized income limit"
    defined_for = StateCode.AL
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        # FY2026 federal amounts, PDF pages 1, 4
        "https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM2025-02_SMIStateTable_Att4.pdf#page=1",
        "https://adeca.alabama.gov/wp-content/uploads/FY-2026-LIHEAP-Manual-1.pdf#page=57",
        "https://liheapch.acf.gov/docs/2026/state-plans/AL_Plan_2026.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.adeca.liheap.eligibility
        # The FY2026 heating season ends before the May 2026 chart update.
        return al_liheap_income_limit_for_lag(
            spm_unit, period, parameters, p.fpg_year_lag
        )
