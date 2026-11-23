from policyengine_us.model_api import *


class nm_premium_assistance_fpl_ratio(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico Premium Assistance income as a share of the poverty line"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.NM
    reference = (
        # 8.401.2.7(G) NMAC defines the FPL, and 8.401.2.11(D)(1)(a) NMAC
        # measures income as in 45 CFR 155.305(f).
        "https://prod-rf-lambda.rtssaas.com/PublicFiles/d89c47bd0d70402dba89b03a22bda6d1/45b8668e-460f-45cd-804f-92ee3d442343/8.401.2.html",
        # 45 CFR 155.300(a): the Exchange's FPL.
        "https://www.govinfo.gov/content/pkg/CFR-2025-title45-vol2/pdf/CFR-2025-title45-vol2-sec155-300.pdf#page=2",
    )
    documentation = (
        "Household income as an exact share of the federal poverty line, the "
        "one New Mexico ratio the premium assistance income limits read: ACA "
        "MAGI, with negative income counted as zero, over aca_fpg. Unlike "
        "aca_magi_fraction it is not truncated to whole percentage points. "
        "8.401.2.7(G) NMAC defines the FPL as the HHS level 'for the "
        "applicable coverage year for the health insurance exchange', which "
        "is the prior-year guideline aca_fpg holds (45 CFR 155.300(a)), and "
        "8.401.2.11(D)(1)(a) NMAC measures income as in 45 CFR 155.305(f), "
        "the section 36B household income aca_magi holds. A tax unit with no "
        "guideline gets an infinite ratio, as in aca_magi_fraction. The "
        "quotient is taken in float64 and stored in float32; for the 100%, "
        "200% and 400% limits, which are powers of two, that rounding cannot "
        "move a ratio of the stored income and guideline onto or across a "
        "limit."
    )

    def formula(tax_unit, period, parameters):
        magi = max_(tax_unit("aca_magi", period), 0).astype(np.float64)
        guideline = tax_unit("aca_fpg", period)
        has_guideline = guideline > 0
        ratio = magi / where(has_guideline, guideline, 1)
        return where(has_guideline, ratio, np.inf)
