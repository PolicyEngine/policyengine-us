from policyengine_us.model_api import *
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class aca_magi_fraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA-related modified AGI as fraction of prior-year FPL"
    documentation = (
        "ACA-related MAGI as a fraction of the federal poverty line for the "
        "year before the coverage year, for the family size and state of "
        "residence in the coverage year, truncated to whole percentage points."
    )
    reference = (
        # PDF pages 8-9: Line 4 (state of residence, prior-year guideline,
        # Alaska and Hawaii tables) and Worksheet 2 (truncation).
        "https://www.irs.gov/pub/irs-prior/i8962--2025.pdf#page=8",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-1#h",
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        magi = max_(0, tax_unit("aca_magi", period))
        # The credit measures income against the guideline for the year before
        # the coverage year (26 U.S.C. 36B(d)(3)(B)). For coverage in the
        # first modeled year, that year precedes the model, so the coverage
        # year's guideline stands in and nothing is computed for an unmodeled
        # year. For that one year the fraction uses a later guideline than
        # 36B(d)(3)(B) calls for.
        guideline_period = period.last_year
        if guideline_period.start.year < FIRST_MODELED_YEAR:
            guideline_period = period
        # Only the guideline lags. Family size is the coverage year's (26 CFR
        # 1.36B-1(d)(1)), and so is the state: Form 8962 Line 4 uses the
        # guideline for "your state of residence" in the coverage year, so
        # Alaska and Hawaii households use their own guidelines. 1.36B-1(h)
        # applies the higher guideline when the residence moves into or out of
        # Alaska or Hawaii during the year, or spouses live in different
        # states; the model has one household state a year and uses the first
        # member's household.
        size = tax_unit("tax_unit_size", period)
        state_group = tax_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, guideline_period, parameters)
        # HHS defines no guideline for Puerto Rico, Guam or the Virgin
        # Islands, whose placeholder is 0, and no Exchange operates there
        # (26 U.S.C. 36B(c)(2)(A)). Their fraction is infinite, above every
        # income limit that reads it.
        has_guideline = guideline > 0
        fraction = magi / where(has_guideline, guideline, 1)
        return where(has_guideline, np.floor(100 * fraction) / 100, np.inf)
