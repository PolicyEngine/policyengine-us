from policyengine_us.model_api import *

MONTHS_IN_QUARTER = 3


class ma_employee_paid_leave_contribution_rate(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts employee paid leave contribution rate"
    documentation = (
        "Annual effective rate of the Massachusetts Paid Family and Medical "
        "Leave contribution that the employer may withhold from wages: the "
        "employee share of the family leave rate plus the employee share of "
        "the medical leave rate (M.G.L. c. 175M s. 6(c)-(e)). Contributions "
        "began October 1, 2019, so the annual rate averages the rates in "
        "effect at the start of each calendar quarter, assuming wages accrue "
        "evenly over the year. Every rate change so far began a quarter, so "
        "this equals the average over all twelve months."
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
        quarter_starts = period.get_subperiods(MONTH)[::MONTHS_IN_QUARTER]
        total = 0
        for quarter_start in quarter_starts:
            p = parameters(quarter_start).gov.states.ma.tax.payroll.paid_leave
            total = total + (
                p.family_rate * p.family_employee_share
                + p.medical_rate * p.medical_employee_share
            )
        return total / len(quarter_starts)
