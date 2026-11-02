from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class dc_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the DC LIHEAP"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = (
        "https://doee.dc.gov/liheap",
        "https://www.law.cornell.edu/uscode/text/42/8624",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hhs.liheap
        p_dc = parameters(period).gov.states.dc.doee.liheap
        state_median_income = spm_unit("hhs_smi", period)
        # The income concept is not clearly defined, assuming IRS gross income
        income = add(spm_unit, period, ["irs_gross_income"])
        smi_limit = state_median_income * p.smi_limit
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below 110%
        # of the poverty guideline. The 60% SMI limit falls below that floor from
        # household size 34 to 39 in 2022 to 2024.
        size = spm_unit("spm_unit_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            size, state_group, period, parameters, year_lag=p_dc.fpg_year_lag
        )
        floor = np.round(guideline * p.fpg_floor, 2)
        return (income <= smi_limit) | (income < floor)
