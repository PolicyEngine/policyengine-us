from policyengine_us.model_api import *


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
        "to the modeled prior-year values, which may be zero."
    )

    def formula(tax_unit, period, parameters):
        prior_period = period.offset(-2, "year")
        return add(
            tax_unit,
            prior_period,
            ["adjusted_gross_income", "tax_exempt_interest_income"],
        )
