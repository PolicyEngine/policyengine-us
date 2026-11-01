from policyengine_us.model_api import *


class is_snap_work_registration_exempt_employed(Variable):
    value_type = bool
    entity = Person
    label = "Exempt from SNAP work registration by working 30 hours weekly or earning the equivalent"
    definition_period = MONTH
    documentation = (
        "Whether the person is exempt from SNAP work registration as an "
        "employed or self-employed person working at least 30 hours weekly "
        "or earning weekly at least the federal minimum wage under 29 U.S.C. "
        "206(a)(1) times 30 hours (7 U.S.C. 2015(d)(2)(E); 7 CFR "
        "273.7(b)(1)(vii)). The exemption also removes the person from the "
        "ABAWD time limit (7 U.S.C. 2015(o)(3)(D)). Hours and earnings are "
        "annual weekly averages (snap_work_requirement_weekly_hours and "
        "snap_work_requirement_weekly_earnings) applied to every month, so "
        "the variable is defined monthly for a later monthly allocation. "
        "Known limitations: averaging misclassifies people near the 30-hour "
        "threshold, and a part-year worker whose annual earnings reach the "
        "minimum wage x 30 hours x 52 weeks is exempt in every month."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2015#d_2",
        "https://www.law.cornell.edu/cfr/text/7/273.7#b_1_vii",
        "https://www.law.cornell.edu/uscode/text/29/206#a_1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.work_requirements.general
        weekly_hours = person("snap_work_requirement_weekly_hours", period.this_year)
        weekly_earnings = person(
            "snap_work_requirement_weekly_earnings", period.this_year
        )
        # 7 U.S.C. 2015(d)(2)(E) uses the same thirty hours in both prongs.
        earnings_threshold = (
            parameters(period).gov.dol.minimum_wage * p.weekly_hours_threshold
        )
        return (weekly_hours >= p.weekly_hours_threshold) | (
            weekly_earnings >= earnings_threshold
        )
