from policyengine_us.model_api import *


class ok_liheap_countable_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Oklahoma LIHEAP countable personal income before deductions"
    defined_for = StateCode.OK
    # OAC 340:20-1-11(a)-(b). The same personal sources apply before
    # ordinary eligibility and before ineligible-member income deeming.
    reference = (
        "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html",
        # Section 1.9 of the FY2025, FY2026 and FY2027 plans.
        "https://liheapch.acf.gov/docs/2025/state-plans/OK_Plan_2025.pdf#page=6",
        "https://liheapch.acf.gov/docs/2026/state-plans/OK_Plan_2026.pdf#page=6",
        "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/okdhs-pdf-library/adult-and-family-services/DETAILED%20MODEL%20PLAN%2010_01_2026.pdf#page=6",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.liheap.income.sources
        income = person("ok_liheap_countable_earned_income", period)
        # Each source is floored at zero, so a loss in one source cannot
        # offset another.
        for source in p.unearned:
            # SSI is monthly; ADD annualizes it exactly once here. Other
            # listed streams are disjoint annual personal income inputs.
            income = income + max_(add(person, period, [source], options=[ADD]), 0)
        # Plan Section 1.9 checks "Excluding MediCare deduction" for Social
        # Security in FY2025-FY2027, so the benefit is counted net of the
        # Part B premium the person pays. medicare_part_b_premium is zero for
        # a person who is not enrolled and excludes the share a Medicare
        # Savings Program pays. OAC 340:20-1-11(a) uses gross income before
        # recoupment or garnishment and is silent on premium withholding.
        premium = person("medicare_part_b_premium", period)
        social_security = max_(person("social_security", period) - premium, 0)
        # TANF is an SPM aggregate and is counted separately once.
        return income + social_security
