from policyengine_us.model_api import *


class aca_magi_fraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA-related modified AGI as fraction of prior-year FPL"
    documentation = (
        "Household income as a fraction of the prior-year federal poverty "
        "line for the premium tax credit tax family (Form 8962 line 5), "
        "truncated to whole percentage points as Worksheet 2 instructs."
    )
    reference = (
        # PDF pages 8-9: line 4 (prior-year poverty line for the line 1
        # family size) and line 5 Worksheet 2 (truncation).
        "https://www.irs.gov/pub/irs-prior/i8962--2025.pdf#page=8",
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        magi = max_(0, tax_unit("aca_magi", period))
        fpg = tax_unit("aca_fpg", period)
        return np.floor(100 * magi / fpg) / 100
