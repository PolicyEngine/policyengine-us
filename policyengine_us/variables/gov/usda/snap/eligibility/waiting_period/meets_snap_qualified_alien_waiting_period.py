from policyengine_us.model_api import *


class meets_snap_qualified_alien_waiting_period(Variable):
    value_type = bool
    entity = Person
    label = "Meets the SNAP qualified alien waiting period"
    documentation = (
        "Whether the person satisfies the SNAP qualified alien waiting period "
        "of 8 USC 1612(a)(2)(L) and 7 CFR 273.4(a)(6)(iii). False only for a "
        "person whose immigration status is subject to the waiting period "
        "(lawful permanent resident, parolee for at least one year or "
        "conditional entrant), who has fewer than the required years in "
        "qualified alien status, and who meets no exception in "
        "is_snap_alien_waiting_period_exempt. Refugees, asylees, people whose "
        "deportation or removal is withheld, and Cuban and Haitian entrants "
        "are exempt by status. The clock is years_since_us_entry, which SNAP "
        "reads as cumulative years in qualified alien status since the "
        "person first obtained it (FNS Question and Answer #1 REVISED, "
        "Question 4); the input must already reflect nonconsecutive periods "
        "and the six-month absence rule of 273.4(a)(6)(iii), and year-of-entry "
        "data overstate it for people who adjusted from a visa or "
        "unauthorized status, which under-applies the waiting period. "
        "273.4(a)(6)(iii) sets no entry-date limit, so there is no carve-out "
        "for people who entered before August 22, 1996. years_since_us_entry "
        "defaults to 0, so a lawful permanent resident, parolee or "
        "conditional entrant without that input is inside the waiting period "
        "unless an exception applies; supply it for anyone who has completed "
        "the waiting period. Until the input data supply years in qualified "
        "alien status (PolicyEngine/microcosm#1085 for the national pool, "
        "PolicyEngine/microcosm#1020 for the ACS local lane), "
        "microsimulation treats everyone in a subject status as inside the "
        "waiting period unless an exception applies. Not modeled: battered "
        "aliens and trafficking victims, who have no immigration status "
        "value, and the "
        "exemption of Afghan (paroled July 31, 2021, to September 30, 2023) "
        "and Ukrainian (paroled February 24, 2022, to September 30, 2024) "
        "humanitarian parolees before P.L. 119-21, who are modeled as "
        "subject like other PAROLED_ONE_YEAR parolees."
    )
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/8/1612#a_2_L",
        "https://www.law.cornell.edu/cfr/text/7/273.4#a_6_iii",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility-qas1.pdf#page=2",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility-qas1.pdf#page=3",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.eligibility.waiting_period
        status = person("immigration_status", period.this_year).decode_to_str()
        subject = np.isin(status, p.subject_immigration_statuses)
        years = person("years_since_us_entry", period.this_year)
        completed = years >= p.years
        exempt = person("is_snap_alien_waiting_period_exempt", period)
        return ~subject | completed | exempt
