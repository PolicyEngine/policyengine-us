from policyengine_us.model_api import *


class wa_tanf_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Washington TANF immigration status eligible"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        "https://www.law.cornell.edu/uscode/text/8/1613",
        # WAC 388-424-0006: bar-exempt qualified alien categories.
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-424-0006",
        # WAC 388-424-0010: five-year bar applicability.
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-424-0010",
    )
    # KNOWN LIMITATION (WAC 388-424-0006): qualified aliens who entered the
    # US before Aug 22, 1996 and continuously resided are NOT subject to the
    # 5-year bar. PolicyEngine's default years_since_us_entry of 5 makes
    # most pre-1996 entrants pass the past_bar check trivially, but a
    # household-calculator user who supplies a low years_since_us_entry for
    # a pre-1996 LPR would be incorrectly classified as still within the
    # 5-year bar. This pre-1996 grandfather is not separately modeled.

    def formula(person, period, parameters):
        status = person("immigration_status", period.this_year)
        status_str = status.decode_to_str()
        is_citizen = status == status.possible_values.CITIZEN

        p = parameters(period).gov.hhs.tanf
        is_bar_exempt = np.isin(status_str, p.bar_exempt_immigration_statuses)

        is_qualified = person("is_citizen_or_legal_immigrant", period.this_year)
        years_in_us = person("years_since_us_entry", period.this_year)
        past_bar = years_in_us >= p.five_year_bar_years

        return is_citizen | is_bar_exempt | (is_qualified & past_bar)
