from policyengine_us.model_api import *


class meets_snap_abawd_work_requirements(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for SNAP benefits via Able-Bodied Adult Without Dependents (ABAWD) work requirements"
    definition_period = MONTH
    documentation = (
        "Whether the person meets the Able-Bodied Adult Without Dependents "
        "(ABAWD) work requirements or is exempt from them. Modeling "
        "simplification (3-in-36 time limit): under 7 CFR 273.24(b), a "
        "noncompliant ABAWD loses eligibility only after receiving benefits "
        "for 3 countable months within a 36-month period; eligibility can be "
        "regained by working 80 hours in a 30-day period (273.24(d)), and "
        "individuals who regain and then lose work qualify for one additional "
        "3-consecutive-month allotment per 36-month period (273.24(e)). The "
        "model does not track month-counting histories, so it treats "
        "noncompliance as immediate monthly ineligibility. This is a "
        "steady-state assumption: it is accurate for ABAWDs who have already "
        "exhausted their 3 countable months, but overstates ineligibility "
        "for new noncompliance spells. The overstatement is largest in "
        "FY2026, when HR1 (P.L. 119-21) restarts time-limit clocks for newly "
        "covered populations. The work test compares average weekly hours "
        "(worked plus work program) times 52 / 12 with 80 hours a month, the "
        "7 CFR 273.24(a)(1)(i) definition of 20 hours a week averaged "
        "monthly; hours worked are averaged over the year, so the result "
        "applies to every month (see snap_work_requirement_weekly_hours)."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.24",
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=11",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.work_requirements.abawd
        # Work activity — 7 U.S.C. 2015(o)(2); 7 CFR 273.24(a)(1):
        # (i) work 20 hours per week averaged monthly, which 273.24(a)(1)(i)
        # defines as 80 hours a month, (ii) participate in and comply with a
        # qualifying work program 20+ hours per week, or (iii) any
        # combination. Hours worked are usual weekly hours averaged over all
        # weeks of the year (snap_work_requirement_weekly_hours), since
        # survey data lack monthly work histories; weekly hours convert to a
        # monthly total at 52 / 12 weeks per month.
        weekly_hours_worked = person(
            "snap_work_requirement_weekly_hours", period.this_year
        )
        work_program_hours = person("weekly_snap_work_program_hours", period.this_year)
        combined_weekly_hours = weekly_hours_worked + work_program_hours
        monthly_hours = combined_weekly_hours * WEEKS_IN_YEAR / MONTHS_IN_YEAR
        meets_hours_threshold = monthly_hours >= p.monthly_hours_threshold
        # (iv) participate in and comply with a workfare program under
        # 7 CFR 273.7(m), which satisfies the requirement regardless of hours.
        is_workfare_participant = person(
            "is_snap_workfare_participant", period.this_year
        )
        is_working = meets_hours_threshold | is_workfare_participant
        # A person satisfies the ABAWD requirement if they are
        # working/compliant OR exempt from the time limit. The full exemption
        # set (age, disability, pregnancy, work-registration exemptions,
        # Indian status, discretionary and area waivers, and the pre-HR1 and
        # good-faith-window variations) lives in is_snap_abawd_exempt so the
        # subject-to-ABAWD status can be reused (e.g. by the Medicaid
        # community engagement pass-through).
        is_exempt = person("is_snap_abawd_exempt", period)
        return is_working | is_exempt
