from policyengine_us.model_api import *


class medicaid_ltss_needs_based_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS needs-based income"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Each person's own gross monthly unearned income from needs-based "
        "sources, before qualified income trust deposits. It is a subset "
        "of medicaid_ltss_gross_unearned_income and defaults to zero. "
        "The model subtracts the needs-based deposited source component "
        "and combines spouses' remaining amounts when couple budgeting "
        "applies. The Delaware general income exclusion does not reduce "
        "the remaining needs-based income. The existing veterans_benefits "
        "variable mixes needs-based pensions and other payments, so "
        "it cannot determine this source classification."
    )
    reference = (
        "https://dhss.delaware.gov/wp-content/uploads/sites/11/2026/06/2026-SSI-Related-Income-Standards-and-Medicare-Premiums.pdf#page=1",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=9",
    )
