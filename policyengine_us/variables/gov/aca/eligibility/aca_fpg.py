from policyengine_us.model_api import *
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR
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
        # Line 1 (tax family size) and line 4 (poverty line).
        "https://www.irs.gov/pub/irs-prior/i8962--2025.pdf#page=8",
    )
    documentation = (
        "Form 8962 line 4: the prior year's poverty guideline for the tax "
        "year's tax family size on line 1 (aca_tax_family_size). The 2013 "
        "guidelines support coverage from 2014. Coverage in 2014 and 2015 "
        "uses residence in the coverage year; later years retain the "
        "existing prior-year residence lookup. A return with no tax family "
        "uses the whole tax unit's size as a numerical convention."
    )

    def formula(tax_unit, period, parameters):
        family_size = tax_unit("aca_tax_family_size", period)
        size = where(family_size > 0, family_size, tax_unit("tax_unit_size", period))
        # Lag the guideline date without lowering the wider model's floor.
        guideline_period = period.last_year
        if guideline_period.start.year < FIRST_PTC_GUIDELINE_YEAR:
            guideline_period = period
        state_period = guideline_period
        if state_period.start.year < FIRST_MODELED_YEAR:
            # Form 8962 line 4 uses coverage-year residence. Historical
            # households need not supply geography for an earlier year.
            state_period = period
        state_group = tax_unit.household("state_group_str", state_period)
        year_lag = period.start.year - guideline_period.start.year
        return fpg(size, state_group, period, parameters, year_lag=year_lag)
