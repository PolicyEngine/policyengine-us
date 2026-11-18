from policyengine_us.model_api import *


class is_federal_medicaid_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Person meets the federal Medicaid immigration status test"
    documentation = (
        "Whether a person's immigration status allows federally funded Medicaid: "
        "a citizen, a qualified noncitizen who is exempt from or past the "
        "five-year bar, or a lawfully residing child or pregnant person in a "
        "state that takes the option in 42 U.S.C. 1396b(v)(4). State-funded "
        "coverage is left to is_medicaid_immigration_status_eligible. "
        "Because this variable is YEAR-defined, the status list dated "
        "2026-10-01 is read at January 1, so the 42 U.S.C. 1396b(v)(5) "
        "narrowing that starts October 1, 2026 applies in the model only from "
        "2027. The test also assumes every state covers qualified noncitizens "
        "who are exempt from or past the bar, though 8 U.S.C. 1612(b)(1) lets "
        "each state decide."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396b#v",
        "https://www.law.cornell.edu/uscode/text/42/1396b#v_4_A",
        "https://www.law.cornell.edu/uscode/text/8/1641",
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title8-section1613&num=0&edition=prelim",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()

        eligible_immigration_status = np.isin(
            immigration_status_str, p.eligible_immigration_statuses
        )
        citizen = immigration_status == immigration_status.possible_values.CITIZEN
        bar_exempt_status = np.isin(
            immigration_status_str, p.bar_exempt_immigration_statuses
        )
        years_since_entry = person("years_since_us_entry", period.this_year)
        past_five_year_bar = years_since_entry >= p.five_year_bar_years
        federally_eligible_status = citizen | (
            eligible_immigration_status & (bar_exempt_status | past_five_year_bar)
        )
        # 42 USC 1396b(v)(4) lets states cover lawfully residing children and
        # pregnant individuals without the qualified-alien limit or five-year bar.
        lawfully_residing_option_eligible = person(
            "is_medicaid_lawfully_residing_option_eligible", period
        )
        return federally_eligible_status | lawfully_residing_option_eligible
