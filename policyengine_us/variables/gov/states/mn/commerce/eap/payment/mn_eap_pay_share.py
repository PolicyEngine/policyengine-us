from policyengine_us.model_api import *


class mn_eap_pay_share(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = "/1"
    label = "Minnesota EAP share of energy cost paid"
    defined_for = StateCode.MN
    reference = (
        # PDF pages 102, 124
        "https://mn.gov/commerce-stat/pdfs/ffy26-eap-policy-manual.pdf#page=102",
        # PDF pages 103, 126
        "https://mn.gov/commerce-stat/pdfs/ffy27-eap-policy-manual.pdf#page=103",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/MN_BenefitMatrix_2026.xlsx",
        "https://mn.gov/commerce-stat/xls/phb-calculator.xlsx",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mn.commerce.eap
        share = p.payment.share
        income = spm_unit("mn_eap_countable_income", period)
        limit = spm_unit("mn_eap_income_limit", period)
        # Qualified Eligibility places households whose only income is DWP,
        # General Assistance, MFIP or SSI at the lowest income level, read here
        # as an income percentile of zero. Amounts are compared to the cent so
        # that summation order does not decide the test.
        qualified_income = add(spm_unit, period, p.income.qualified_eligibility_sources)
        qualified_only = (qualified_income > 0) & (
            np.round(income, 2) <= np.round(qualified_income, 2)
        )
        # The income percentile is income over the limit for the household
        # size; annual equivalents give the same ratio as monthly amounts.
        ratio = np.divide(income, limit, out=np.zeros_like(income), where=limit > 0)
        percentile = where(qualified_only, 0, ratio)
        # Appendix 4A pays the maximum share up to the slope start, falls
        # linearly to the minimum share at the slope end, and stays there.
        progress = clip(
            (percentile - share.slope_start) / (share.slope_end - share.slope_start),
            0,
            1,
        )
        return share.maximum - (share.maximum - share.minimum) * progress
