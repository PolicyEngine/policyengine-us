from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit, smi
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ar_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Arkansas LIHEAP annualized income limit"
    defined_for = StateCode.AR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        # FY2026 federal amounts
        "https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM2025-02_SMIStateTable_Att4.pdf#page=1",
        "https://liheapch.acf.gov/docs/2026/state-plans/AR_Plan_2026.pdf#page=9",
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Eligibility-Chart_2026.pdf",
        "https://liheapch.acf.gov/docs/2025/state-plans/AR_Plan_2025.pdf#page=8",
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Eligibility-Chart_2025.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ee.aeo.liheap.income.limit
        size = spm_unit("ar_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        monthly_smi = smi(size, state, period, parameters) * p.smi_rate / MONTHS_IN_YEAR
        state_group = spm_unit.household("state_group_str", period)
        capped_size = clip(size, 1, p.max_table_size)
        guideline = fpg(
            capped_size, state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        monthly_fpg = guideline * p.fpg_rate / MONTHS_IN_YEAR
        monthly_base = where(size <= p.smi_max_size, monthly_smi, monthly_fpg)
        # Half-up monthly rounding reproduces the published FY2025 and FY2026
        # tables; it is a reconciled numerical pattern, not an express rule.
        rounding = p.rounding_increment
        rounded_base = np.floor(monthly_base / rounding + 0.5) * rounding
        # The charts add a printed amount for each person above size 20.
        extra_people = max_(size - p.max_table_size, 0)
        monthly_limit = rounded_base + extra_people * p.additional_member_amount
        # 42 U.S.C. 8624(b)(2)(B) pays no household above the greater of 60% of
        # state median income, in the amounts HHS publishes by household size,
        # and 150% of the poverty guideline. A published monthly amount that
        # rounds above that maximum stops there.
        p_hhs = parameters(period).gov.hhs.liheap
        smi_maximum = liheap_smi_limit(size, state, p_hhs.smi_limit, period, parameters)
        fpg_maximum = p_hhs.fpg_limit * fpg(
            max_(size, 1), state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        limit = min_(monthly_limit * MONTHS_IN_YEAR, max_(smi_maximum, fpg_maximum))
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below
        # 110% of the poverty guideline. In 2025-2027 every limit stays at
        # least 32% above that floor at every household size (in 2025 and 2027,
        # the printed per-member amount above size 20 sets the narrowest
        # margin), so no separate floor is applied.
        return where(size > 0, limit, 0)
