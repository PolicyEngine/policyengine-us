from policyengine_us.model_api import *


class sd_ssp_care_joint_entry(Variable):
    value_type = bool
    entity = Person
    label = "Both spouses entered South Dakota long-term care this month"
    definition_period = MONTH
    reference = (
        "https://sdlegislature.gov/Rules/Administrative/67:46:05:30",
        "https://sdlegislature.gov/Rules/Administrative/67:46:04:10",
    )
    documentation = "True only for the calendar month in which both spouses entered a long-term care facility, such as assisted living or adult foster care. In that month the couple's combined resources are tested against the joint resource limit (ARSD 67:46:05:30), and the couple's combined gross income is shared equally between the spouses before each spouse's deductions (ARSD 67:46:04:10(6), applied through 67:46:06:03). Set it for both spouses, and leave it false for later months, when each spouse is budgeted as a separate individual. A month in which only one spouse enters care is not covered by this flag."
