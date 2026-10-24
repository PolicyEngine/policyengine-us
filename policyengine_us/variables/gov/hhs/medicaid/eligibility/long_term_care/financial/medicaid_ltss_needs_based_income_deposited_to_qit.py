from policyengine_us.model_api import *


class medicaid_ltss_needs_based_income_deposited_to_qit(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS needs-based unearned income deposited to a qualified income trust"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Each person's own monthly needs-based unearned income validly "
        "deposited into a qualified income trust. This source component "
        "is part of medicaid_ltss_unearned_income_deposited_to_qit, rather "
        "than an additional deposit. Defaults to zero. The model caps it "
        "at both gross needs-based income and total unearned deposits "
        "when computing the needs-based income remaining outside the "
        "trust. Trust and deposit validity are unmodeled."
    )
    reference = (
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=9",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=54",
    )
