from policyengine_us.model_api import *

EMPLOYER_ADDITIONAL_STATE_PAYROLL_TAX_COMPONENTS = [
    "ca_employer_additional_state_payroll_tax",
    "co_employer_additional_state_payroll_tax",
    "dc_employer_additional_state_payroll_tax",
    "de_employer_additional_state_payroll_tax",
    "ma_employer_additional_state_payroll_tax",
    "me_employer_additional_state_payroll_tax",
    "or_employer_additional_state_payroll_tax",
    "ri_employer_additional_state_payroll_tax",
    "vt_employer_additional_state_payroll_tax",
    "wa_employer_additional_state_payroll_tax",
]


class employer_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer additional state payroll taxes and contributions"
    documentation = (
        "Employer-side mandatory state payroll taxes and payroll-funded "
        "contributions other than state unemployment insurance."
    )
    definition_period = YEAR
    unit = USD
    adds = EMPLOYER_ADDITIONAL_STATE_PAYROLL_TAX_COMPONENTS
