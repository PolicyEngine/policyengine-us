from policyengine_us.model_api import *
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR


class aca_magi_fraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA-related modified AGI as fraction of prior-year FPL"
    documentation = (
        "ACA-related MAGI as fraction of federal poverty line. The first "
        "reference documents the use of the prior-year FPL; the second "
        "documents the truncation of the fraction."
    )
    reference = (
        dict(
            title="2022 IRS Form 8962 (ACA PTC) instructions, Line 4",
            href="https://www.irs.gov/pub/irs-pdf/i8962.pdf#page=7",
        ),
        dict(
            title="2022 IRS Form 8962 instructions, Line 5 Worksheet 2",
            href="https://www.irs.gov/pub/irs-pdf/i8962.pdf#page=8",
        ),
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
        fpg = tax_unit("tax_unit_fpg", guideline_period)
        return np.floor(100 * magi / fpg) / 100
