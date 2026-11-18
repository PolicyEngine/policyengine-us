from policyengine_us.model_api import *


class medicare_irmaa_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicare IRMAA MAGI applied in the benefit year"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1395r#i_4_B"
    documentation = (
        "Modified adjusted gross income that the Medicare Part B and Part D "
        "income-related monthly adjustment amounts apply to in the benefit "
        "year. The law uses the income from two years earlier "
        "(medicare_irmaa_magi_two_years_prior). When "
        "gov.simulation.medicare_irmaa_uses_current_year_income is true, the "
        "benefit year's own income is used instead "
        "(medicare_irmaa_tax_year_magi), so the charges move with that year's "
        "earnings."
    )

    def formula(tax_unit, period, parameters):
        if parameters(period).gov.simulation.medicare_irmaa_uses_current_year_income:
            return tax_unit("medicare_irmaa_tax_year_magi", period)
        return tax_unit("medicare_irmaa_magi_two_years_prior", period)
