from policyengine_us.model_api import *


class ri_rimap_fpl_ratio(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island Marketplace Affordability Program income as a share of the federal poverty line"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = (
        "https://webserver.rilegislature.gov/statutes/TITLE42/42-157.2/42-157.2-4.htm",
        "https://healthsourceri.com/wp-content/uploads/2027-RIMAP-Final-Parameters.pdf#page=3",
    )
    documentation = (
        "Household income (ACA MAGI) as a share of the federal poverty line "
        "for the premium tax credit tax family (aca_fpg, the prior-year "
        "guideline). R.I. Gen. Laws 42-157.2-4(c) ties the program to "
        "eligibility for the federal premium tax credit, so the program uses "
        "that credit's household income and poverty line. The exact ratio, "
        "not the truncated aca_magi_fraction, decides the 200% and 400% "
        "edges and the place within the 150-200% band, which the Plan Year "
        "2027 parameters make proportional to the household's position in "
        "the band. Negative income counts as zero. A household with no "
        "poverty guideline gets an infinite ratio, as in aca_magi_fraction; "
        "every Rhode Island household has one."
    )

    def formula(tax_unit, period, parameters):
        magi = max_(tax_unit("aca_magi", period), 0).astype(np.float64)
        guideline = tax_unit("aca_fpg", period)
        # aca_fpg is 0 where HHS defines no guideline. Divide by 1 there to
        # avoid dividing by zero, then return an infinite ratio, as
        # aca_magi_fraction does.
        has_guideline = guideline > 0
        # The quotient is computed in float64, but core stores float
        # variables as float32, so the cast is lost on return and other
        # variables read the float32 rounding of the ratio. That is safe at
        # the 200% and 400% limits: for whole-dollar guidelines (household
        # sizes 1 to 15 checked), the float32 incomes just above and just
        # below 2 or 4 times the guideline still store ratios on the same
        # side of the limit, so nobody is misclassified.
        ratio = magi / where(has_guideline, guideline, 1)
        return where(has_guideline, ratio, np.inf)
