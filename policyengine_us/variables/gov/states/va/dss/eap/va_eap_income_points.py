from policyengine_us.model_api import *


class va_eap_income_points(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Virginia EAP income points"
    documentation = "Benefit points from countable income as a whole percent of the income limit for the household size: 25 points from 0% to 19%, falling to 1 point from 95% to 100%. Income above the limit, reachable only when every member receives SSI, scores 0 points."
    # The Complete Manual's copy of this page (01/03) still bases the table on
    # 130% of the guidelines; the 05/21 page in the benefit matrix controls.
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/VA_BenefitMatrix_2026.pdf#page=6",
        # PDF pages 31, 52
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/eap/Complete_Manual.pdf#page=31",
    )
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.eap.points
        # The percent uses countable income after the $50 medical deduction.
        # This is an inference: Appendix B does not name the income, but the
        # system deducts the medical amount "to determine the countable income
        # for screening purposes" (manual D.4, page 52), and B.6.c (page 31)
        # calls it a "programmatic income disregard".
        income = spm_unit("va_eap_countable_income", period)
        limit = spm_unit("va_eap_income_limit", period)
        # Appendix B: "The system calculates the percentage of the maximum
        # income level for the household's income to determine the point
        # assignment." The quotient is formed in float64 and the percent is
        # rounded to four decimals before the whole-percent floor. Incomes are
        # stored as float32, so an exact band start such as 40% can arrive as
        # 39.999999%; four decimals absorb that error while one dollar below a
        # band start (at least 0.0005% for any limit up to $200,000) stays
        # below it.
        share = np.divide(
            income.astype(np.float64),
            limit,
            out=np.zeros(income.shape),
            where=limit > 0,
        )
        # NOTE: 100 converts the share to a percent; the band edges are whole
        # percents in the parameter.
        percent = np.floor(np.round(share * 100, 4))
        return where(limit > 0, p.income.calc(percent), 0)
