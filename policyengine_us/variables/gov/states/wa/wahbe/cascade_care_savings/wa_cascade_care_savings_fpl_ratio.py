from policyengine_us.model_api import *


class wa_cascade_care_savings_fpl_ratio(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Washington Cascade Care Savings income as a share of the federal poverty line"
    )
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/rcw/default.aspx?cite=43.71.110",
        # Final PY2027 policy: Section 3(9) and 3(11) (the Federal Poverty
        # Level of 26 U.S.C. 36B(d)(3)(B) and household income under
        # 36B(d)(2)), p.2; Section 4(1)(c) (the 250% limit), p.3; Section
        # 4(12) (income of the tax-filing household) and Section 5(1)(b) (the
        # 200% split of the federally subsidized amount), p.6.
        # PDF pages 2-3, 6
        "https://www.wahbexchange.org/content/dam/materials/communications/policy/2026/Final_PY_2027_Cascade_Care_Savings_Policy.pdf#page=2",
    )
    documentation = (
        "Household income (ACA MAGI per 26 U.S.C. 36B(d)(2)) of the tax-filing "
        "household as a share of the federal poverty line for the premium tax "
        "credit tax family (aca_fpg, the prior-year guideline). Cascade Care "
        "Savings uses this exact ratio, not the truncated aca_magi_fraction, "
        "for both its 250% income limit and, from PY2027, the 200% split "
        "between the two amounts for members with federal subsidies, so the "
        "limit and the split are decided on the same ratio. Negative income "
        "counts as zero. A household with no poverty guideline gets an "
        "infinite ratio, as in aca_magi_fraction, which fails the income limit."
    )

    def formula(tax_unit, period, parameters):
        # Section 3(9) defines the Federal Poverty Level by 26 U.S.C.
        # 36B(d)(3)(B), so the poverty line is aca_fpg, the same line that
        # aca_magi_fraction and the federal credit divide by.
        magi = max_(tax_unit("aca_magi", period), 0).astype(np.float64)
        guideline = tax_unit("aca_fpg", period)
        # aca_fpg is 0 where HHS defines no guideline. Divide by 1 there to
        # avoid dividing by zero, then return an infinite ratio, which is
        # above every limit, as aca_magi_fraction does.
        has_guideline = guideline > 0
        # Divide in float64: a float32 quotient can round a ratio just above
        # a limit down onto it. The result is stored as float32, but for a
        # whole-dollar guideline the smallest float32 income above 2.00 or
        # 2.50 times the guideline still rounds to a stored ratio above it.
        ratio = magi / where(has_guideline, guideline, 1)
        return where(has_guideline, ratio, np.inf)
