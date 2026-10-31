from policyengine_us.model_api import *


class medicaid_ltss_is_initial_eligibility_determination(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid LTSS initial eligibility determination"
    definition_period = MONTH
    default_value = True
    documentation = (
        "Whether the modeled month is an initial LTSS eligibility "
        "determination. Defaults to initial eligibility, when current "
        "resources of both spouses are tested after the community spouse "
        "resource allowance. Set false only for months after eligibility "
        "was established during the same continuous LTSS period. In those "
        "months, community spouse resources are not deemed available and "
        "the applicant's own countable resources are tested against the "
        "individual resource limit under 42 USC 1396r-5(c)(4). This input "
        "affects only applicants with a community spouse. In Washington, "
        "set true again for a new determination after a break of at least "
        "30 consecutive days, and supply the new most-recent-period "
        "snapshot under WAC 182-513-1350(3)(b)(vi)(A) and 182-513-1355."
    )
    reference = (
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title42/html/USCODE-2024-title42-chap7-subchapXIX-sec1396r-5.htm",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=71",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1350",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1355",
    )
