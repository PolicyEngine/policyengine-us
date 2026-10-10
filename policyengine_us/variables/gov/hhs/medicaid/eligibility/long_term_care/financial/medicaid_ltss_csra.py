from policyengine_us.model_api import *


class medicaid_ltss_csra(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS community spouse resource allowance"
    unit = USD
    quantity_type = STOCK
    definition_period = MONTH
    documentation = (
        "Modeled community spouse resource allowance before court or "
        "fair-hearing adjustments. Texas and Delaware apply their floor, "
        "half of the first-period snapshot, and federal cap. Washington "
        "selects its statutory branch from the actual year and month in "
        "which the most recent continuous institutionalization began: "
        "before October 1989 there is no CSRA allocation; October 1989 "
        "through July 2003 uses the federal maximum; August 2003 onward "
        "uses Washington's floor, half of the beginning-month snapshot, "
        "and federal cap. The historical pre-1989 resource counting rule "
        "is implemented separately in the resource eligibility screen. "
        "The allowance is informational during continuing eligibility, "
        "when the modern resource screen tests applicant resources alone."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396r-5#f_2",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=69",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1355",
    )

    def formula_2026_01_01(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care.financial
        state = person.household("state_code", period)
        states = state.possible_values
        washington = state == states.WA
        floor = select(
            [state == states.TX, state == states.DE, washington],
            [
                p.federal.csra.minimum,
                max_(p.de.csra.state_minimum, p.federal.csra.minimum),
                max_(p.wa.csra.state_minimum, p.federal.csra.minimum),
            ],
            default=0,
        )
        snapshot = where(
            washington,
            person(
                "wa_medicaid_ltss_couple_countable_resources_at_most_recent_institutionalization",
                period,
            ),
            person(
                "medicaid_ltss_couple_countable_resources_at_first_institutionalization",
                period,
            ),
        )
        modern = min_(max_(snapshot / 2, floor), p.federal.csra.maximum)
        start_year = person(
            "wa_medicaid_ltss_most_recent_institutionalization_start_year", period
        )
        start_month = person(
            "wa_medicaid_ltss_most_recent_institutionalization_start_month", period
        )
        onset = start_year * 100 + start_month
        # WAC 182-513-1355(2)(a), (3)(a), and (3)(b). Both statutory
        # boundaries are the first day of the month, so year/month suffices.
        allowance = select(
            [washington & (onset < 198910), washington & (onset < 200308)],
            [0, p.federal.csra.maximum],
            default=modern,
        )
        has_spouse = person("medicaid_ltss_has_community_spouse", period)
        supported = (state == states.TX) | (state == states.DE) | washington
        valid_onset = (
            (start_year >= 1)
            & (start_month >= 1)
            & (start_month <= 12)
            & (onset <= period.start.year * 100 + period.start.month)
        )
        return where(has_spouse & supported & (~washington | valid_onset), allowance, 0)
