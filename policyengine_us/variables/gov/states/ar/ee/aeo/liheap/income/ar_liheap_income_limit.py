from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ar_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Arkansas LIHEAP annualized income limit"
    defined_for = StateCode.AR
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/AR_Plan_2026.pdf#page=9",
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Eligibility-Chart_2026.pdf",
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
        additional_guideline = (
            fpg(
                capped_size + 1,
                state_group,
                period,
                parameters,
                year_lag=p.fpg_year_lag,
            )
            - guideline
        )
        monthly_fpg = guideline * p.fpg_rate / MONTHS_IN_YEAR
        monthly_increment = additional_guideline * p.fpg_rate / MONTHS_IN_YEAR
        monthly_base = where(size <= p.smi_max_size, monthly_smi, monthly_fpg)
        # Half-up monthly rounding reproduces the published FY2026 table;
        # it is a reconciled numerical pattern, not an express rounding rule.
        # The chart separately adds $688 for each person above size 20.
        rounding = p.rounding_increment
        rounded_base = np.floor(monthly_base / rounding + 0.5) * rounding
        rounded_increment = np.floor(monthly_increment / rounding + 0.5) * rounding
        extra_people = max_(size - p.max_table_size, 0)
        monthly_limit = rounded_base + extra_people * rounded_increment
        return where(size > 0, monthly_limit * MONTHS_IN_YEAR, 0)
