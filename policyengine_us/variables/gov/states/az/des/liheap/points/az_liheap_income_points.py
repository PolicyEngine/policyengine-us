from policyengine_us.model_api import *


class az_liheap_income_points(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Arizona LIHEAP income points"
    documentation = (
        "Benefit matrix points from countable income as a share of the income "
        "limit for the household size: 0% to 20% gives 5 points, 21% to 40% 4, "
        "41% to 60% 3, 61% to 80% 2, 81% to 100% 1, and above 100% (reachable "
        "only through categorical eligibility) 0."
    )
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/AZ_BenefitMatrix_Heating_2026.pdf#page=1",
        "https://des.az.gov/liheap",
        # PDF pages 10, 40
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=10",
    )
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.des.liheap.points
        income = spm_unit("az_liheap_countable_income", period)
        limit = spm_unit("az_liheap_income_limit", period)
        # DES: "Total Monthly Gross Income Divided by the Monthly Gross Income
        # Limit for the Household Size = % Income"; annual over annual gives the
        # same ratio. A zero limit (no eligible member) is treated as a ratio
        # above every band, scoring 0 points. The quotient is formed in float64
        # so that an exact band top such as 10,884 / 54,420 = 0.20 stays in its
        # band instead of rounding above the threshold.
        ratio = np.divide(
            income.astype(np.float64),
            limit,
            out=np.full(income.shape, np.inf),
            where=limit > 0,
        )
        # Band tops: "0% - 20%" is 5 points and the DES example places 44% in
        # the 41% to 60% band, so right=True with the -inf first threshold.
        return p.income_ratio.calc(ratio, right=True)
