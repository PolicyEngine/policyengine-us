from policyengine_us.model_api import *

EMPLOYEE_STATE_PAYROLL_TAX_COMPONENTS = [
    "ca_employee_state_payroll_tax",
    "co_employee_state_payroll_tax",
    "ct_employee_state_payroll_tax",
    "de_employee_state_payroll_tax",
    "ma_employee_state_payroll_tax",
    "me_employee_state_payroll_tax",
    "nj_employee_state_payroll_tax",
    "ny_employee_state_payroll_tax",
    "or_employee_state_payroll_tax",
    "ri_employee_state_payroll_tax",
    "vt_employee_state_payroll_tax",
    "wa_employee_state_payroll_tax",
]


class employee_state_payroll_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Employee state payroll taxes and contributions"
    documentation = (
        "Employee-side mandatory state payroll taxes and payroll-funded "
        "contributions, aggregated from jurisdiction-specific rules."
    )
    definition_period = YEAR
    unit = USD
    adds = EMPLOYEE_STATE_PAYROLL_TAX_COMPONENTS
