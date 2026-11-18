from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class tn_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Tennessee LIHEAP income limit"
    defined_for = StateCode.TN
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/TN_Plan_2026.pdf#page=8",
        "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/LIHEAP-2026-Policy-Manual-for-Tennessee.pdf#page=24",
        "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/2026-LIHEAP-Eligible-Income-Household-Size-Benefits.pdf",
        # PDF pages 9, 12
        "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/DETAILED-MODEL-PLAN-LIHEAP_10_01_2026.pdf#page=9",
        "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/DRAFT-LIHEAP-2027-Policy-Manual-7-11-2026.pdf#page=27",
        # PDF pages 1-4
        "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/2027-LIHEAP-LI-12-Eligible-Income-Benefit-Matrix.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tn.thda.liheap.eligibility
        size = spm_unit("tn_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        state_group = spm_unit.household("state_group_str", period)
        # The HHS floor order reproduces the FY2026 matrix ceilings for sizes
        # 1-12 (size 8 is printed as $85,064.50) and the FY2027 ceilings for
        # sizes 1-8. FY2027 sizes 9 and over use 150% of the 2026 guideline,
        # rounded down to the nearest dollar; the printed size 13-16 ceilings
        # are below that amount and are not used.
        smi_limit = liheap_smi_limit(size, state, p.smi_rate, period, parameters)
        fpg_rate = p.fpg_rate.calc(size)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        fpg_limit = np.floor(guideline * fpg_rate)
        limit = where(fpg_rate > 0, fpg_limit, smi_limit)
        return where(size > 0, limit, 0)
