from policyengine_us.model_api import *
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR


def previous_year_wages(person, period, parameters):
    """Hawaii TDI wages in the year before ``period``.

    These follow hi_temporary_disability_insurance_wages without its state
    test, since households often enter a state for the simulation year alone.
    Pay comes from employment_income_before_lsr, where situations and datasets
    store employment income, so the earlier year calculates no labor supply
    response. Before the first modeled year, only inputs for that year count:
    nothing is calculated or cached for an unmodeled year, and a value the
    simulation calculated for it earlier stays out, so the order of
    calculation doesn't change the answer.
    """
    last_year = period.last_year
    excluded = parameters(
        last_year
    ).gov.states.hi.tax.payroll.temporary_disability_insurance.excluded_payments
    if last_year.start.year >= FIRST_MODELED_YEAR:
        pay = person("employment_income_before_lsr", last_year)
        excluded_pay = add(person, last_year, excluded)
    else:
        simulation = person.simulation

        def provided(variable):
            holder = simulation.get_holder(variable)
            if last_year not in holder.get_input_periods(simulation.branch_name):
                return person.empty_array()
            return holder.get_array(last_year, simulation.branch_name)

        pay = provided("employment_income_before_lsr")
        excluded_pay = sum(provided(variable) for variable in excluded)
    return max_(pay - excluded_pay, 0)


class hi_temporary_disability_insurance_qualified(Variable):
    value_type = bool
    entity = Person
    label = "Wages count toward the Hawaii temporary disability insurance contribution"
    documentation = (
        "HRS 392-43(b)(1) counts wages from a payroll period only if the prior "
        "52 weeks hold enough wages and enough weeks with enough paid hours. "
        "This annual proxy passes a worker in either of two ways. The first "
        "tests the simulation year's wages, weeks worked and usual weekly "
        "hours, and there zero weeks or zero hours mean the value went "
        "unreported, so that part of the test passes. The second tests the "
        "previous year's wages, weeks worked and usual weekly hours, and it "
        "needs all three on file. A single year of inputs leaves the previous "
        "year at zero, so a worker with a short year and no history on file "
        "does not pass. The previous year's wages leave out what the wage "
        "definition leaves out, such as military basic pay, but skip its "
        "state test, so a worker new to Hawaii can pass on wages earned "
        "elsewhere. They come from employment_income_before_lsr. Simulation "
        "moves situation inputs of employment_income there, but pay set on "
        "employment_income with set_input after the simulation is built stays "
        "out of the previous year's wages, so enter it on "
        "employment_income_before_lsr. Before 2015, the first year the model "
        "covers, only inputs for that year count, so a deferral counts only "
        "when entered as the contribution itself, such as "
        "traditional_401k_contributions, not as the desired amount. Weeks and "
        "hours count all work, self-employment included. Usual weekly hours "
        "stand in for each week's hours, so a worker whose usual hours fall "
        "under the minimum does not pass even with enough qualifying weeks."
    )
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://data.capitol.hawaii.gov/hrscurrent/Vol07_Ch0346-0398/HRS0392/HRS_0392-0043.htm",
        "https://data.capitol.hawaii.gov/hrscurrent/Vol07_Ch0346-0398/HRS0392/HRS_0392-0043_0005.htm",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.hi.tax.payroll.temporary_disability_insurance.qualification
        wages = person("hi_temporary_disability_insurance_wages", period)
        weeks = person("weeks_worked", period)
        hours = person("weekly_hours_worked_before_lsr", period)
        meets_wages = wages >= p.minimum_wages
        meets_weeks = (weeks == 0) | (weeks >= p.minimum_weeks)
        meets_hours = (hours == 0) | (hours >= p.minimum_weekly_hours)
        passes_in_year = meets_wages & meets_weeks & meets_hours
        # The previous year passes only on positive evidence, because zero
        # there means no history on file. Weeks and hours count all work, so
        # that year's wages must also clear the minimum: a year of military
        # basic pay or self-employment holds no Hawaii covered wages.
        last_year = period.last_year
        weeks_last_year = person("weeks_worked", last_year)
        hours_last_year = person("weekly_hours_worked_before_lsr", last_year)
        wages_last_year = previous_year_wages(person, period, parameters)
        passes_last_year = (
            (wages_last_year >= p.minimum_wages)
            & (weeks_last_year >= p.minimum_weeks)
            & (hours_last_year >= p.minimum_weekly_hours)
        )
        return passes_in_year | passes_last_year
