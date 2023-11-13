from policyengine_us.model_api import *


class aca_magi_percent(Variable):
    value_type = int
    entity = TaxUnit
    label = "ACA-related modified AGI as percent of prior-year FPL"
    documentation = (
        "ACA-related MAGI as percent of federal poverty line."
        "Documentation on use of prior-year FPL in the following reference:"
        "  title: 2022 IRS Form 8962 (ACA PTC) instructions, Line 4"
        "  href: https://www.irs.gov/pub/irs-pdf/i8962.pdf#page=7"
        "Documentation on truncation of percent in the following reference:"
        "  title: 2022 IRS Form 8962 instructions, Line 5 Worksheet 2"
        "  href: https://www.irs.gov/pub/irs-pdf/i8962.pdf#page=8"
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        magi = max_(0, tax_unit("aca_magi", period))
        fpg = tax_unit("tax_unit_fpg", period.last_year)
        return np.floor(100.0 * magi / fpg)
