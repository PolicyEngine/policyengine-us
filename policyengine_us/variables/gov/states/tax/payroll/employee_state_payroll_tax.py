from policyengine_us.model_api import *

EMPLOYEE_STATE_PAYROLL_TAX_COMPONENTS = [
    "ca_employee_state_payroll_tax",
    "co_employee_state_payroll_tax",
    "ct_employee_state_payroll_tax",
    "de_employee_state_payroll_tax",
    "ma_employee_state_payroll_tax",
    "me_employee_state_payroll_tax",
    "mn_employee_state_payroll_tax",
    "nj_employee_state_payroll_tax",
    "ny_employee_state_payroll_tax",
    "or_employee_state_payroll_tax",
    "pa_employee_state_payroll_tax",
    "ri_employee_state_payroll_tax",
    "vt_employee_state_payroll_tax",
    "wa_employee_state_payroll_tax",
]


class employee_state_payroll_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Employee state payroll taxes and contributions"
    documentation = (
        "Employee-side state payroll taxes and payroll-funded contributions, "
        "aggregated from jurisdiction-specific rules. Most components are "
        "contributions the statute puts on the worker and requires the "
        "employer to withhold: California SDI, Connecticut Paid Leave, New "
        "Jersey TDI, FLI, UI and workforce contributions, Paid Leave Oregon "
        "and the Oregon statewide transit tax, Pennsylvania UC, Rhode Island "
        "TDI and WA Cares. The rest are premiums the statute puts on the "
        "employer, which may deduct up to a share from wages without being "
        "required to: Colorado FAMLI, Delaware Paid Leave, Maine and "
        "Massachusetts Paid Family and Medical Leave, Minnesota Paid Leave, "
        "New York Paid Family Leave and Disability Benefits, the Vermont "
        "Child Care Contribution and Washington Paid Family and Medical "
        "Leave. For those, the employee amount is the permitted share times "
        "employer_state_payroll_premium_deduction_share, which defaults to 1, "
        "the full permitted share; the employer-side variables carry any part "
        "the employer does not deduct."
    )
    definition_period = YEAR
    unit = USD
    adds = EMPLOYEE_STATE_PAYROLL_TAX_COMPONENTS
