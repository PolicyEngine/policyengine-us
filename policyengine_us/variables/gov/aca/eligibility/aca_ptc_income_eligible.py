from policyengine_us.model_api import *


class aca_ptc_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Household income meets the ACA premium tax credit income test"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/36B#c_1_A",
        # Worksheet 2 (line 5): compare household income with 400% of the
        # poverty line in dollars, then truncate the percentage.
        "https://www.irs.gov/pub/irs-prior/i8962--2025.pdf#page=9",
    )
    documentation = (
        "Whether household income passes the premium tax credit income "
        "scale (gov.aca.ptc_income_eligibility), not counting the "
        "below-poverty exception for lawfully present immigrants. 26 U.S.C. "
        "36B(c)(1)(A) covers income that 'equals or exceeds 100 percent but "
        "does not exceed 400 percent' of the poverty line, so both edges are "
        "inclusive. Form 8962 Worksheet 2 first asks whether household income "
        "is more than four times the poverty line, in dollars, and only then "
        "drops the decimals of the percentage for line 5. The scale's "
        "brackets start at their thresholds, so evaluating it on the "
        "truncated aca_magi_fraction alone excluded income exactly at 400% of "
        "the poverty line. A truncated fraction equal to a threshold is "
        "exactly at it only when truncation dropped nothing; such income "
        "keeps the eligible side of the boundary."
    )

    def formula(tax_unit, period, parameters):
        scale = parameters(period).gov.aca.ptc_income_eligibility
        # Form 8962 line 5: the percentage with decimals dropped.
        magi_frac = tax_unit("aca_magi_fraction", period)
        # Worksheet 2 compares the dollar amounts, so income exactly at a
        # threshold is distinguished from income up to one point above it.
        # Divide in float64, by the poverty line aca_magi_fraction uses: a
        # float32 quotient can round a ratio just above 400% down onto it.
        magi = max_(tax_unit("aca_magi", period), 0).astype(np.float64)
        guideline = tax_unit("aca_fpg", period)
        # A territory has no guideline and an infinite fraction, which a
        # right-closed lookup would place in the scale's top bracket.
        has_guideline = guideline > 0
        exact_magi_frac = magi / where(has_guideline, guideline, 1)
        at_whole_percentage = has_guideline & (exact_magi_frac <= magi_frac)
        # The scale's brackets start at their thresholds, which is right for
        # the 100% floor ("equals or exceeds"). At a ceiling ("does not
        # exceed"), income exactly at the threshold stays in the bracket
        # below it, which a right-closed evaluation returns.
        return scale.calc(magi_frac) | (
            at_whole_percentage & scale.calc(magi_frac, right=True)
        )
