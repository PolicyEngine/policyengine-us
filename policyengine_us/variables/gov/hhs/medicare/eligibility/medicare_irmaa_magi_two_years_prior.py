from policyengine_us.model_api import *
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR


class medicare_irmaa_magi_two_years_prior(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicare IRMAA MAGI from two years prior"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1395r"
    documentation = (
        "Modified adjusted gross income used to determine Medicare IRMAA "
        "charges. Callers may provide this value directly for the current "
        "benefit year. When it is not provided, PolicyEngine computes it as "
        "adjusted gross income plus tax-exempt interest from two years prior. "
        "Single-year datasets without lagged income inputs therefore default "
        "to the modeled prior-year values, which may be zero. For benefit "
        "years whose income year two years prior precedes the first year "
        "PolicyEngine models (2015), it is zero unless provided."
    )

    def formula(tax_unit, period, parameters):
        prior_period = period.offset(-2, "year")
        if prior_period.start.year < FIRST_MODELED_YEAR:
            # Benefit years 2015 and 2016 would read 2013 and 2014 income,
            # before the parameters (and so the income formulas) begin.
            # Return zero, the value the formula yields in later years when
            # no prior-year income is provided, rather than computing any
            # variable for a period the model does not cover.
            return tax_unit.empty_array()
        return add(
            tax_unit,
            prior_period,
            ["adjusted_gross_income", "tax_exempt_interest_income"],
        )
