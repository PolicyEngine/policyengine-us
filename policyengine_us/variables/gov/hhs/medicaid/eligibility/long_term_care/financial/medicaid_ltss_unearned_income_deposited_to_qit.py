from policyengine_us.model_api import *


class medicaid_ltss_unearned_income_deposited_to_qit(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS unearned income deposited to a qualified income trust"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Each person's own monthly unearned income validly deposited "
        "into a qualified income trust. Defaults to no deposits. The "
        "model excludes these deposits from gross unearned income without "
        "allowing a negative remainder. The Texas opening-month rule can "
        "also exclude an entire identified source after verification of "
        "subsequent full deposits. Trust legality, irrevocability, "
        "funding, payback terms, and the validity of a deposit are unmodeled."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396p#d_4_B",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=54",
    )
