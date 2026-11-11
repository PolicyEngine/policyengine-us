from policyengine_us.model_api import *


class cbo_medicare_benefit(Variable):
    value_type = float
    entity = Person
    label = "CBO Medicare benefit"
    documentation = (
        "PolicyEngine values Medicare Parts A, B and D in CBO household "
        "income at average spending per enrollee, less premium income and the "
        "Part D low-income subsidy. The Medicare Trustees count premiums that "
        "enrollees or others pay on their behalf, including premiums state "
        "Medicaid programs pay. PolicyEngine's state Medicaid spending totals "
        "include these buy-ins, so PolicyEngine nets them here to avoid "
        "counting them twice. CBO counts Medicaid-paid premiums as Medicare "
        "spending. CBO assigns every enrollee the same average and counts the "
        "Part D low-income subsidy separately as a means-tested transfer. "
        "PolicyEngine subtracts average premium income and subsidy costs per "
        "Medicare enrollee rather than the person's own premiums."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.cbo.gov/system/files/2026-01/61910-DOHI-health.pdf#page=27",
        # PDF pages 27, 39
        "https://www.cbo.gov/system/files/2024-09/60341-income.pdf#page=27",
        # PDF pages 46, 52
        "https://www.cbo.gov/system/files/2018-07/54234-workingpaper.pdf#page=46",
    )
    defined_for = "medicare_enrolled"

    def formula(person, period, parameters):
        p = parameters(period).calibration.gov.hhs.medicare
        premiums = p.premium_income_per_enrollee
        total_premiums = premiums.part_a + premiums.part_b + premiums.part_d
        net = (
            p.per_capita_cost
            - total_premiums
            - p.part_d_low_income_subsidy_per_enrollee
        )
        return max_(net, 0)
