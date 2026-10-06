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
        "to the modeled prior-year values, which may be zero. When the year "
        "two years prior precedes the first year PolicyEngine models (2015), "
        "only income provided for that year counts, and the rest is zero."
    )

    def formula(tax_unit, period, parameters):
        prior_period = period.offset(-2, "year")
        if prior_period.start.year >= FIRST_MODELED_YEAR:
            return add(
                tax_unit,
                prior_period,
                ["adjusted_gross_income", "tax_exempt_interest_income"],
            )
        # Benefit years 2015 and 2016 look back to 2013 and 2014, before the
        # parameters begin, so income for those years cannot be computed. Use
        # income provided for them and treat the rest as zero, the value the
        # formula yields in later years when no prior-year income is provided.
        # Reading stored values computes and caches nothing for those years.
        simulation = tax_unit.simulation

        def provided(variable, population):
            holder = simulation.get_holder(variable)
            value = holder.get_array(prior_period, simulation.branch_name)
            return population.empty_array() if value is None else value

        agi = provided("adjusted_gross_income", tax_unit)
        tax_exempt_interest = tax_unit.sum(
            provided("tax_exempt_interest_income", tax_unit.members)
        )
        return agi + tax_exempt_interest
