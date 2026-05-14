from policyengine_us.model_api import *


class wa_rca_immigration_window_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Washington RCA immigration and ORR-window eligible"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-466-0120",
        "https://www.ecfr.gov/current/title-45/subtitle-B/chapter-IV/part-400/subpart-J/section-400.211",
    )
    # NOTE: For asylees and Cuban-Haitian entrants, per 45 CFR 400.211(b),
    # years_since_us_entry should encode years-since-status-grant rather
    # than years-since-physical-entry.

    def formula(person, period, parameters):
        immigration_eligible = person("wa_rca_immigration_status_eligible", period)
        window_years = parameters(
            period.this_year
        ).gov.hhs.orr.refugee_assistance_window_years
        within_window = person("years_since_us_entry", period.this_year) < window_years
        return immigration_eligible & within_window
