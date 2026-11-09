from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


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
        # Form 8962 line 4 uses the current tax family's size and residence
        # with the prior year's guideline, not the prior year's family facts.
        size = tax_unit("tax_unit_size", period)
        state_group = tax_unit.household("state_group_str", period)
        prior_year_fpg = fpg(size, state_group, period, parameters, year_lag=1)
        return np.floor(100 * magi / prior_year_fpg) / 100
