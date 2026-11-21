from policyengine_us.model_api import *

MONTHS_IN_QUARTER = 3


class ma_employer_paid_leave_contribution_rate(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts employer paid leave contribution rate"
    documentation = (
        "Annual effective rate of the employer's share of the Massachusetts "
        "Paid Family and Medical Leave contribution: the parts of the family "
        "and medical leave rates the employer may not deduct from wages, for "
        "employers with 25 or more covered individuals (employer headcount is "
        "the proxy). Contributions began October 1, 2019, so the annual rate "
        "averages the rates in effect at the start of each calendar quarter, "
        "assuming wages accrue evenly over the year. Every rate change so far "
        "began a quarter, so this equals the average over all twelve months."
    )
    definition_period = YEAR
    unit = "/1"
    defined_for = StateCode.MA
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXXII/Chapter175M/Section6",
        "https://malegislature.gov/Laws/SessionLaws/Acts/2026/Chapter101",
        "https://web.archive.org/web/20190716144139/https://www.mass.gov/news/notice-to-massachusetts-employers-about-pfml-delay",
    )

    def formula(person, period, parameters):
        headcount = person("employer_headcount", period)
        quarter_starts = period.get_subperiods(MONTH)[::MONTHS_IN_QUARTER]
        total = 0
        for quarter_start in quarter_starts:
            p = parameters(quarter_start).gov.states.ma.tax.payroll.paid_leave
            rate = p.family_rate * (1 - p.family_employee_share) + p.medical_rate * (
                1 - p.medical_employee_share
            )
            liable = headcount >= p.employer_headcount_threshold
            total = total + where(liable, rate, 0)
        return total / len(quarter_starts)
