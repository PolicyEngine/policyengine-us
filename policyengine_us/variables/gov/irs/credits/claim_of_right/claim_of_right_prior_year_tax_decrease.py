from policyengine_us.model_api import *


class claim_of_right_prior_year_tax_decrease(Variable):
    value_type = float
    entity = TaxUnit
    label = "Prior-year tax decrease from excluding repaid claim of right income"
    unit = USD
    documentation = (
        "Decrease in the filers' federal income tax under chapter 1 of the "
        "Internal Revenue Code for the earlier year or years that would "
        "result solely from excluding from gross income all the income they "
        "repaid this year (claim_of_right_repayment): the chapter 1 tax "
        "previously determined, after credits and including the alternative "
        "minimum tax, less that tax refigured without the repaid income. It "
        "leaves out the net investment income tax, self-employment tax and "
        "payroll taxes."
    )
    definition_period = YEAR
    reference = (
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapQ-partV-sec1341.htm",
        # 26 CFR 1.1341-1(b)(1)(ii) and (d)(4)
        "https://www.ecfr.gov/current/title-26/chapter-I/subchapter-A/part-1/subject-group-ECFR4c74bc8cf7c11fb/section-1.1341-1",
        # Publication 525 (2025), Repayments, method 2, steps 2 and 3
        "https://www.irs.gov/pub/irs-prior/p525--2025.pdf#page=36",
    )
