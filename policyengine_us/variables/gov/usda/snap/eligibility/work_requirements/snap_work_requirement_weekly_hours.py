from policyengine_us.model_api import *


class snap_work_requirement_weekly_hours(Variable):
    value_type = float
    entity = Person
    label = "Weekly hours worked for SNAP work requirements"
    unit = "hour"
    definition_period = YEAR
    documentation = (
        "Usual weekly hours in the weeks worked, averaged over all weeks of "
        "the year (usual hours x weeks worked / 52). It is an annual proxy "
        "for the monthly ABAWD test of 20 hours a week averaged monthly, "
        "which 7 CFR 273.24(a)(1)(i) defines as 80 hours a month, and for "
        "the 30-hour work registration exemption (7 CFR 273.7(b)(1)(vii)), "
        "because survey data record usual hours and weeks worked for the "
        "year rather than monthly work. weekly_hours_worked_before_lsr "
        "keeps its meaning of usual hours for the other programs that read "
        "it. When weeks_worked is 0 (not reported or did not work) usual "
        "hours are used unchanged, so datasets and households without weeks "
        "worked see no change; an explicit 0 for a worker is also read as a "
        "full year. Setting gov.simulation.snap_work_tests_average_over_year "
        "to false returns usual hours. Known limitations: averaging "
        "misclassifies people near the thresholds, for example 40 hours for "
        "26 weeks averages 20 hours a week and passes in every month although "
        "only about six months had work; the averaged value applies to every "
        "month of the year, and a monthly allocation of work is deferred to "
        "PolicyEngine/policyengine-us#8967. Archived datasets that already "
        "stored annualized hours (usual hours x weeks worked / 52, as "
        "policyengine-us-data did before March 2026) would be deflated twice."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2015#o_2",
        "https://www.law.cornell.edu/cfr/text/7/273.24#a_1_i",
        "https://www.law.cornell.edu/cfr/text/7/273.7#b_1_vii",
    )

    def formula(person, period, parameters):
        usual_hours = person("weekly_hours_worked_before_lsr", period)
        if not parameters(period).gov.simulation.snap_work_tests_average_over_year:
            return usual_hours
        weeks = person("weeks_worked", period)
        averaged_hours = usual_hours * min_(weeks, WEEKS_IN_YEAR) / WEEKS_IN_YEAR
        # NOTE: coherent survey data pair positive usual hours with positive
        # weeks, so zero weeks means "not reported" and keeps usual hours.
        return where(weeks > 0, averaged_hours, usual_hours)
