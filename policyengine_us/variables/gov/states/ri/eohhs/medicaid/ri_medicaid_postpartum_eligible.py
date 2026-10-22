from policyengine_us.model_api import *


class ri_medicaid_postpartum_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Rhode Island postpartum Medicaid continuation"
    definition_period = MONTH
    defined_for = StateCode.RI
    reference = (
        "https://webserver.rilegislature.gov/Statutes/TITLE42/42-12.3/42-12.3-3.htm"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ri.eohhs.medicaid
        coverage = person("ri_pregnancy_coverage", period.this_year)
        eligible_during_pregnancy = coverage != coverage.possible_values.NONE
        pregnancy_end = person("ri_medicaid_pregnancy_end_date", period.this_year)
        reference_date = np.datetime64(period.start.date)
        # The first day after the anniversary month is an exclusive endpoint.
        # Month arithmetic preserves the full final month, including leap years.
        first_uncovered_month = (
            pregnancy_end.astype("datetime64[M]") + p.postpartum_coverage_months + 1
        )
        return (
            (p.postpartum_coverage_months > 0)
            & eligible_during_pregnancy
            & (pregnancy_end <= reference_date)
            & (reference_date.astype("datetime64[M]") < first_uncovered_month)
        )
