from functools import reduce

from policyengine_us.model_api import *
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR
from policyengine_us.variables.gov.hhs.medicare.eligibility.medicare_irmaa_tax_year_magi import (
    PERSON_ADDITIONS,
    TAX_UNIT_ADDITIONS,
)

# Per-capita CBO AGI: the series that extends a single-year dataset's dollar
# inputs to later years when they have no series of their own
# (DEFAULT_MICRODATA_UPRATING, divided by population). Deflating by it runs
# that projection backward.
LOOKBACK_DEFLATOR = (
    "calibration.gov.cbo.income_by_source.adjusted_gross_income_per_capita"
)


def index_at(index, instant):
    """The index at ``instant``, held at its first value before the series
    begins, as policyengine-core holds an uprating index."""
    value = index(instant)
    # ``values_list`` runs from the latest instant to the earliest.
    return index.values_list[-1].value if value is None else value


class medicare_irmaa_magi_two_years_prior(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicare IRMAA MAGI from two years prior"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395r#i_4",
        "https://www.law.cornell.edu/uscode/text/26/135#c_1",
        "https://www.irs.gov/pub/irs-prior/f8815--2025.pdf#page=3",
    )
    documentation = (
        "Modified adjusted gross income from two years before the benefit "
        "year, which sets Medicare IRMAA charges "
        "(medicare_irmaa_tax_year_magi for that year). Callers may provide "
        "this value directly for the benefit year. "
        "When the simulation holds no input for the year two years prior or "
        "any earlier year, every input would read as its default there, so "
        "PolicyEngine instead uses the IRMAA MAGI of the earliest year it "
        "holds inputs for (no earlier than 2015, the first year it models), "
        "deflated to the year two years prior by "
        "calibration.gov.cbo.income_by_source.adjusted_gross_income_per_capita, "
        "the index that extends single-year datasets to later years. A "
        "single-year dataset thus supplies its own year's income to the two "
        "benefit years whose income year precedes it. Any input supplied for "
        "the year two years prior, or earlier, turns this off: the year's "
        "inputs are then taken as given. "
        "When the earliest input year is the benefit year itself, as for a "
        "household entered for one year or a dataset's own year, the income "
        "two years prior is imputed from the benefit year's income, so the "
        "charges then move with that income in reforms and counterfactual "
        "branches, as they do under "
        "gov.simulation.medicare_irmaa_uses_current_year_income but "
        "deflated. Provide this value, or inputs for the year two years "
        "prior, to hold it fixed. "
        "CBO AGI has no values for 2016 to 2018 and is held at its 2015 "
        "value, so the index drifts down through 2018 and then rises 31% "
        "from 2017 to 2019 and 39% from 2018 to 2020: a household entered "
        "for 2016, 2017 or 2018 alone gets slightly more than that year's "
        "income, and one entered for 2019 or 2020 alone gets that year's "
        "income times 0.765 or 0.721. "
        "When inputs reach back to 2013 or 2014 and the year two years prior "
        "is one of those years, its income cannot be computed: only income "
        "provided for it counts, and the rest is zero."
    )

    def formula(tax_unit, period, parameters):
        prior_period = period.offset(-2, "year")
        first_input_year = earliest_input_year(tax_unit.simulation)
        if first_input_year is None or prior_period.start.year < first_input_year:
            # Inputs start after the year two years prior. Use the earliest
            # year that has them, which may be the benefit year itself.
            source_year = max(
                (period.start.year if first_input_year is None else first_input_year),
                FIRST_MODELED_YEAR,
            )
            source_period = period.offset(source_year - period.start.year, "year")
            magi = tax_unit("medicare_irmaa_tax_year_magi", source_period)
            index = reduce(getattr, LOOKBACK_DEFLATOR.split("."), parameters)
            return (
                magi
                * index_at(index, prior_period.start)
                / index_at(index, source_period.start)
            )
        if prior_period.start.year >= FIRST_MODELED_YEAR:
            return tax_unit("medicare_irmaa_tax_year_magi", prior_period)
        # Inputs reach back to 2013 or 2014, before the parameters begin, so
        # income for those years cannot be computed. Use income provided for
        # them and treat the rest as zero. Reading stored values computes and
        # caches nothing for those years; tax unit roles are the benefit
        # year's.
        simulation = tax_unit.simulation
        filer_amounts = parameters(
            period
        ).gov.irs.ald.filer_amounts_recorded_on_dependents
        dependent = tax_unit.members("is_tax_unit_dependent", period)

        def provided(variable, population):
            holder = simulation.get_holder(variable)
            value = holder.get_array(prior_period, simulation.branch_name)
            if value is None and variable == "section_911_excluded_income":
                # Defaults to the stacking amount, as its formula does.
                return provided("foreign_earned_income_exclusion", population)
            return population.empty_array() if value is None else value

        magi = provided("adjusted_gross_income", tax_unit)
        for variable in TAX_UNIT_ADDITIONS:
            magi = magi + provided(variable, tax_unit)
        for variable in PERSON_ADDITIONS:
            amount = provided(variable, tax_unit.members)
            if variable not in filer_amounts:
                amount = where(dependent, 0, amount)
            magi = magi + tax_unit.sum(amount)
        return magi
