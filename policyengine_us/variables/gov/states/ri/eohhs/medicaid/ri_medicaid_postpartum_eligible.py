from policyengine_us.model_api import *


class ri_medicaid_postpartum_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Rhode Island postpartum Medicaid continuation"
    definition_period = MONTH
    defined_for = StateCode.RI
    reference = (
        "https://webserver.rilegislature.gov/Statutes/TITLE42/42-12.3/42-12.3-3.htm",
        "https://www.law.cornell.edu/uscode/text/42/1396a#e_16",
        "https://www.medicaid.gov/medicaid/spa/downloads/RI-22-0024.pdf#page=7",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ri.eohhs.medicaid
        months = int(p.postpartum_coverage_months)
        coverage = person("ri_pregnancy_coverage", period.this_year)
        eligible_during_pregnancy = coverage != coverage.possible_values.NONE
        pregnancy_end = person("ri_medicaid_pregnancy_end_date", period.this_year)
        reference_date = np.datetime64(period.start.date)
        # 42 U.S.C. 1396a(e)(16) and SPA RI-22-0024 start the 12-month period on
        # the last day of pregnancy, so it ends the day before the same date 12
        # months later, in the month of (end date - 1 day) + 12 months. Coverage
        # runs through the last day of that month.
        day_before_end = pregnancy_end - np.timedelta64(1, "D")
        first_uncovered_month = day_before_end.astype("datetime64[M]") + months + 1
        return (
            (months > 0)
            & eligible_during_pregnancy
            & (pregnancy_end <= reference_date)
            & (reference_date.astype("datetime64[M]") < first_uncovered_month)
        )
