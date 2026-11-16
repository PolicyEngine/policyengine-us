from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg

FIRST_PTC_GUIDELINE_YEAR = 2013


class aca_fpg(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal poverty line for the premium tax credit tax family"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/36B#d_3",
        "https://www.govinfo.gov/content/pkg/USCODE-2014-title26/pdf/USCODE-2014-title26-subtitleA-chap1-subchapA-partIV-subpartC-sec36B.pdf#page=4",
        "https://www.irs.gov/pub/irs-prior/i8962--2014.pdf#page=6",
        "https://www.irs.gov/pub/irs-prior/i8962--2015.pdf#page=7",
        "https://www.irs.gov/pub/irs-prior/i8962--2016.pdf#page=6",
        "https://www.irs.gov/pub/irs-prior/i8962--2017.pdf#page=6",
        # Line 1 (tax family size) and line 4 (poverty line for the state of
        # residence).
        "https://www.irs.gov/pub/irs-prior/i8962--2025.pdf#page=8",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-1#h",
    )
    documentation = (
        "Form 8962 line 4: the prior year's poverty guideline for the tax "
        "year's tax family size on line 1 (aca_tax_family_size) and the tax "
        "year's state of residence. The 2013 guidelines support coverage "
        "from 2014. A return on which every head and spouse can be claimed "
        "elsewhere has no tax family and no applicable taxpayer; as a "
        "numerical convention, not a legal rule, it keeps the guideline for "
        "the whole tax unit. The credit starts in 2014; for an earlier tax "
        "year the formula applies no lag and reads the guideline parameter "
        "at the tax year's own date."
    )

    def formula(tax_unit, period, parameters):
        family_size = tax_unit("aca_tax_family_size", period)
        size = where(family_size > 0, family_size, tax_unit("tax_unit_size", period))
        # The guideline year lags the tax year (26 U.S.C. 36B(d)(3)(B)). The
        # lagged lookup reads a parameter date only, so it reaches the 2013
        # and 2014 guidelines without lowering the wider model's floor. The
        # credit starts in 2014, and an earlier tax year takes no lag.
        guideline_period = period.last_year
        if guideline_period.start.year < FIRST_PTC_GUIDELINE_YEAR:
            guideline_period = period
        # Only the guideline lags. The state is the tax year's: line 4 uses
        # the guideline for "your state of residence" in the tax year, so
        # Alaska and Hawaii households use their own guidelines. A household
        # need not supply geography for the year before. 26 CFR
        # 1.36B-1(h) applies the higher guideline when the residence moves
        # into or out of Alaska or Hawaii during the year, or spouses live in
        # different states; the model has one household state a year and
        # uses the first member's household.
        state_group = tax_unit.household("state_group_str", period)
        return fpg(size, state_group, guideline_period, parameters)
