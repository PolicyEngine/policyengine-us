from policyengine_us.model_api import *


class cbo_medicare_benefit(Variable):
    value_type = float
    entity = Person
    label = "CBO Medicare benefit"
    documentation = (
        "Medicare benefit as the Congressional Budget Office counts it in "
        "household income: the government's average cost per enrollee of "
        "providing Medicare Parts A, B and D, net of premiums paid by or on "
        "behalf of enrollees, excluding costs for institutionalized "
        "enrollees. CBO assigns the same average to every enrollee and "
        "counts the Part D low-income subsidy separately as a means-tested "
        "transfer, so this scales Medicare spending per enrollee net of the "
        "low-income subsidy to enrollees who do not live in nursing homes, "
        "then subtracts per-enrollee premium income, rather than the "
        "person's own premiums."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.cbo.gov/publication/61910",
        "https://www.cbo.gov/system/files/2024-09/60341-income.pdf#page=27",
        "https://www.cbo.gov/system/files/2018-07/54234-workingpaper.pdf#page=46",
        "https://www.cbo.gov/system/files/2018-07/54234-workingpaper.pdf#page=52",
    )
    defined_for = "medicare_enrolled"

    def formula(person, period, parameters):
        p = parameters(period).calibration.gov.hhs.medicare
        premiums = p.premium_income_per_enrollee
        total_premiums = premiums.part_a + premiums.part_b + premiums.part_d
        # CBO removes institutionalized enrollees' share of Medicare benefits
        # other than the low-income subsidy, which it counts separately.
        noninstitutionalized_spending = (
            p.per_capita_cost - p.part_d_low_income_subsidy_per_enrollee
        ) * p.noninstitutionalized_spending_ratio
        return max_(noninstitutionalized_spending - total_premiums, 0)
