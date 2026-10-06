from policyengine_us.model_api import *


class medicaid_ltss_income_disregards_already_applied(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid LTSS income input already reflects every income disregard"
    definition_period = MONTH
    default_value = False
    documentation = (
        "Marks medicaid_ltss_qit_adjusted_income as the final countable "
        "income after every Delaware income disregard, so the model applies "
        "no further disregard. Delaware is the only modeled state with a "
        "disregard before the special income limit test, so the flag has no "
        "effect elsewhere. When false, the model treats the input as gross "
        "income and subtracts the $20 general disregard from its "
        "non-needs-based portion (DSSM 20240.1). That is correct for income "
        "without earnings, and for any income of an applicant with a "
        "community spouse, because DSSM 20990 makes the $20 disregard the "
        "sole deduction for that applicant. Earned income of any other "
        "applicant needs the final amount: DSSM 20240.3 deducts $20, then "
        "$65, then one-half of the remaining gross earnings, and when there "
        "is also unearned income the $20 applies to the unearned income "
        "first, as the most advantageous order."
    )
    reference = (
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=9",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=10",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=71",
    )
