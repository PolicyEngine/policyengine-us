from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class aca_fpg(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal poverty line for the premium tax credit tax family"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/36B#d_3",
        # Line 1 (tax family size) and line 4 (poverty line).
        "https://www.irs.gov/pub/irs-prior/i8962--2025.pdf#page=8",
    )
    documentation = (
        "Form 8962 line 4: the prior year's poverty guideline for the tax "
        "family size on line 1 (aca_tax_family_size). A return on which "
        "every head and spouse can be claimed elsewhere has no tax family and "
        "no applicable taxpayer; it keeps the guideline for the whole tax "
        "unit, so readers that are not about the credit see the same value "
        "as before."
    )

    def formula(tax_unit, period, parameters):
        family_size = tax_unit("aca_tax_family_size", period)
        size = where(family_size > 0, family_size, tax_unit("tax_unit_size", period))
        # The guideline year lags the tax year; the state group is read for
        # the prior year, as the guideline lookup did before.
        state_group = tax_unit.household("state_group_str", period.last_year)
        return fpg(size, state_group, period, parameters, year_lag=1)
