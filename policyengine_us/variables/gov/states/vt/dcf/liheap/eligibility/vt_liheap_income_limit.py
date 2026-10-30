from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class vt_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Vermont LIHEAP annual income limit"
    defined_for = StateCode.VT
    reference = (
        "https://legislature.vermont.gov/statutes/section/33/026/02604",
        # PDF pages 38-39
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2900-Seasonal-Fuel-Assistance.pdf#page=38",
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2913.pdf",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.vt.dcf.liheap
        p_hhs = parameters(period).gov.hhs.liheap
        size = spm_unit("vt_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        state = spm_unit.household("state_code_str", period)
        # Rule 2914(a)(3) reads the maximum from the P-2913 table: 185% of the
        # whole-dollar monthly guideline, rounded half up to the dollar. Monthly
        # income at or below it is the same test as annual income at or below
        # twelve times it.
        monthly_guideline = spm_unit("vt_liheap_fpg", period) / MONTHS_IN_YEAR
        monthly_limit = np.floor(monthly_guideline * p.eligibility.fpg_rate + 0.5)
        guideline = fpg(
            max_(size, 1), state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        # 33 V.S.A. 2604(a) and rule 2913(b) bar income above 185% of the
        # poverty guideline or above the LIHEAP maximum, the greater of 150% of
        # the guideline and 60% of state median income (42 U.S.C.
        # 8624(b)(2)(B)). In FFY2026 the LIHEAP maximum is the lower limit for
        # sizes 10-15, below the 185% amounts printed in P-2913; the code
        # follows the statute and rule.
        smi_limit = liheap_smi_limit(size, state, p_hhs.smi_limit, period, parameters)
        liheap_maximum = max_(guideline * p_hhs.fpg_limit, smi_limit)
        # The statute caps income at exactly 185% of the guideline. The rounded
        # P-2913 amount applies where it is lower (size 1: 2,412 a month against
        # 2,412.71); where it rounds above that (size 2: 3,262 against 3,260.625),
        # the exact 185% applies.
        poverty_limit = min_(
            monthly_limit * MONTHS_IN_YEAR, guideline * p.eligibility.fpg_rate
        )
        limit = min_(poverty_limit, liheap_maximum)
        return where(size > 0, limit, 0)
