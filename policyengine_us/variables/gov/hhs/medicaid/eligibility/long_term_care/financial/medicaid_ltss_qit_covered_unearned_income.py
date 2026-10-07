from policyengine_us.model_api import *


class medicaid_ltss_qit_covered_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Monthly unearned income from sources covered by the Medicaid LTSS qualified income trust"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Actual monthly unearned income from the sources identified in the "
        "qualified income trust instrument, such as the applicant's private "
        "pension. This is a source amount before deposits, and a subset of "
        "medicaid_ltss_gross_unearned_income; it is not a caller-computed "
        "exclusion. Texas can exclude these sources in full in the opening "
        "month when a partial deposit was made and subsequent full deposits "
        "were verified. Report the deposited component separately in "
        "medicaid_ltss_qit_covered_unearned_income_deposited."
    )
    reference = "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust"
