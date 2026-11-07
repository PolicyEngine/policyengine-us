from policyengine_us.model_api import *

MONTHS_IN_QUARTER = 3


class ma_employer_paid_leave_contribution_rate(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts employer paid leave contribution rate"
    documentation = (
        "Annual effective rate of the employer's share of the Massachusetts "
        "Paid Family and Medical Leave medical leave contribution, using "
        "employer headcount as a proxy for covered individuals. Contributions "
        "began October 1, 2019, so the annual rate averages the rates in effect "
        "at the start of each calendar quarter, assuming wages accrue evenly "
        "over the year. Every rate change so far began a quarter, so this "
        "equals the average over all twelve months."
    )
    definition_period = YEAR
    unit = "/1"
    defined_for = StateCode.MA
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXXII/Chapter175M/Section6",
        "https://web.archive.org/web/20190716144139/https://www.mass.gov/news/notice-to-massachusetts-employers-about-pfml-delay",
    )

    def formula(person, period, parameters):
        headcount = person("employer_headcount", period)
        quarter_starts = period.get_subperiods(MONTH)[::MONTHS_IN_QUARTER]
        total = 0
        for quarter_start in quarter_starts:
            p = parameters(quarter_start).gov.states.ma.tax.payroll.paid_leave
            rate = p.medical_rate * (1 - p.medical_employee_share)
            liable = headcount >= p.employer_headcount_threshold
            total = total + where(liable, rate, 0)
        return total / len(quarter_starts)
