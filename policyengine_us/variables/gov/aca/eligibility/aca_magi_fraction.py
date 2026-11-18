from policyengine_us.model_api import *


class aca_magi_fraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA-related modified AGI as fraction of prior-year FPL"
    documentation = (
        "Household income as a fraction of the prior-year federal poverty "
        "line for the premium tax credit tax family and the state of "
        "residence in the coverage year (Form 8962 line 5), truncated to "
        "whole percentage points as Worksheet 2 instructs."
    )
    reference = (
        # PDF pages 8-9: line 4 (prior-year poverty line for the line 1
        # family size and the state of residence) and line 5 Worksheet 2
        # (truncation).
        "https://www.irs.gov/pub/irs-prior/i8962--2025.pdf#page=8",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-1#h",
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        magi = max_(0, tax_unit("aca_magi", period))
        guideline = tax_unit("aca_fpg", period)
        # HHS defines no guideline for Puerto Rico, Guam or the Virgin
        # Islands, whose placeholder is 0, and no Exchange operates there
        # (26 U.S.C. 36B(c)(2)(A); 42 U.S.C. 18024(d)). Their fraction is
        # infinite rather than 0 / 0 (NaN at $0 of income): the eligibility
        # scale's out-of-range cell is false, and the required contribution
        # percentage is capped out to 0. is_aca_marketplace_enrollee excludes
        # them by state group.
        has_guideline = guideline > 0
        # Multiply before dividing, so income exactly on a whole percentage
        # (100 x 36,621 / 15,650 = 234) isn't floored one point low by a
        # quotient that isn't exactly representable.
        percent = 100 * magi / where(has_guideline, guideline, 1)
        return where(has_guideline, np.floor(percent) / 100, np.inf)
