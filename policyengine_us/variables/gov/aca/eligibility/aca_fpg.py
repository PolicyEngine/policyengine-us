from policyengine_us.model_api import *
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class aca_fpg(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal poverty line for the premium tax credit tax family"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/36B#d_3",
        # Line 1 (tax family size) and line 4 (poverty line for the state of
        # residence).
        "https://www.irs.gov/pub/irs-prior/i8962--2025.pdf#page=8",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-1#h",
    )
    documentation = (
        "Form 8962 line 4: the prior year's poverty guideline for the tax "
        "year's tax family size on line 1 (aca_tax_family_size) and the tax "
        "year's state of residence. The former lookup, tax_unit_fpg for the "
        "prior year, also took the household size and state from the prior "
        "year; both now come from the tax year, as lines 1 and 4 require. "
        "A return on which every head and spouse can be claimed "
        "elsewhere has no tax family and no applicable taxpayer; as a "
        "numerical convention, not a legal rule, it keeps the guideline for "
        "the whole tax unit, so readers that are not about the credit see "
        "the same value as before. For the first modeled year, the year "
        "before precedes the model, so the tax year's guideline stands in."
    )

    def formula(tax_unit, period, parameters):
        family_size = tax_unit("aca_tax_family_size", period)
        size = where(family_size > 0, family_size, tax_unit("tax_unit_size", period))
        # The guideline year lags the tax year (26 U.S.C. 36B(d)(3)(B)). For
        # the first modeled year, the year before precedes the model, so the
        # tax year's guideline stands in and nothing is computed for an
        # unmodeled year. For that one year the line uses a later guideline
        # than 36B(d)(3)(B) calls for.
        guideline_period = period.last_year
        if guideline_period.start.year < FIRST_MODELED_YEAR:
            guideline_period = period
        # Only the guideline lags. The state is the tax year's: line 4 uses
        # the guideline for "your state of residence" in the tax year, so
        # Alaska and Hawaii households use their own guidelines. 26 CFR
        # 1.36B-1(h) applies the higher guideline when the residence moves
        # into or out of Alaska or Hawaii during the year, or spouses live in
        # different states; the model has one household state a year and
        # uses the first member's household.
        state_group = tax_unit.household("state_group_str", period)
        return fpg(size, state_group, guideline_period, parameters)
