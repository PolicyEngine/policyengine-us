from policyengine_us.model_api import *


class medicaid_ltss_qit_subsequent_full_deposits_verified(Variable):
    value_type = bool
    entity = Person
    label = "Subsequent full deposits of Medicaid LTSS qualified income trust covered sources have been verified"
    definition_period = MONTH
    default_value = False
    documentation = (
        "Whether staff verified, before certification, that the entire "
        "amounts of the income sources identified in the qualified income "
        "trust are deposited in subsequent months. This is a verification "
        "fact, not a caller-selected eligibility result. Texas requires "
        "this verification before any exclusion for a partial opening-month "
        "deposit. Without it, F-6820 invalidates the trust for this screen, "
        "so both earned and unearned income include deposited amounts. "
        "Full covered-source deposits retain their ordinary exclusion. "
        "Other trust legality and deposit-validity conditions remain "
        "outside this financial screen."
    )
    reference = "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust"
