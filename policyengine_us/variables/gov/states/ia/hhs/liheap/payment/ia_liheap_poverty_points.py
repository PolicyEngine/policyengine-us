from policyengine_us.model_api import *


class ia_liheap_poverty_points(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Iowa LIHEAP poverty level points"
    documentation = (
        "Payment matrix points for the ratio of annual countable income to the "
        "household's federal poverty guideline: 8 points at or below 75 "
        "percent, 6 through 100 percent, 5 through 125 percent and 4 through "
        "200 percent. Appendix I does not say which guideline divides the "
        "income; the manual's only poverty table is Appendix B, so the same "
        "lagged guideline as the income limit is used (an inference). A "
        "household with no counted member has no guideline and scores zero."
    )
    reference = (
        # Appendix B and Appendix I item 1, Poverty Level.
        # PDF pages 89, 137
        "https://hhs.iowa.gov/media/17262/download?inline#page=89",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/IA_BenefitMatrix_Heat-Crisis_2026.pdf#page=1",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.liheap.payment
        # Model arrays are float32; a float32 quotient can land just above a
        # float64 band top and flip an exact 75% into the 76-100% band, so the
        # ratio is formed in float64 before the lookup.
        income = spm_unit("ia_liheap_countable_income", period).astype(np.float64)
        guideline = spm_unit("ia_liheap_fpg", period).astype(np.float64)
        has_guideline = guideline > 0
        ratio = np.divide(
            income, guideline, out=np.zeros_like(income), where=has_guideline
        )
        # Appendix I prints "0 – 75%", "76 – 100%", "101 – 125%", "126 – 200%"
        # with the note "Poverty levels of .01% are rounded up to the next
        # percentage": a ratio of exactly 0.75 is 75% (8 points) and 0.7501
        # becomes 76% (6 points). The scale is keyed at the band tops with a
        # -.inf first threshold, so right=True reproduces the rounding exactly.
        # A household with no guideline (no counted member) has no poverty
        # level and scores zero points; it is ineligible in any case.
        return where(has_guideline, p.poverty_points.calc(ratio, right=True), 0)
