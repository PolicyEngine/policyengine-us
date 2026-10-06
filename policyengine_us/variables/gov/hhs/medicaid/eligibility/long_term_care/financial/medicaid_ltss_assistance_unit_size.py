from policyengine_us.model_api import *


class medicaid_ltss_assistance_unit_size(Variable):
    value_type = int
    entity = Person
    label = "Medicaid LTSS assistance unit size"
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Explicit size of the assistance unit used by the Medicaid LTSS "
        "financial threshold screen. It is not inferred from a tax unit, "
        "household, or marital unit. Use 2 only when the state budgets "
        "both spouses as a couple: in Texas, spouses in the same "
        "institutional setting (MEPD G-6120; 1 TAC 358.436); in Delaware, "
        "spouses requesting or receiving institutional services in the "
        "same facility, who may choose couple or individual budgeting after "
        "six months there (DSSM 20810). Otherwise, including an applicant "
        "with a community spouse, use 1. At size 2, each spouse's income "
        "and resource inputs carry the couple's combined totals, which are "
        "compared with the couple limits. Zero and unsupported sizes are "
        "fail-closed."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.602",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/g-6100-institutional-eligibility-budgets",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-358-436",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=67",
    )
