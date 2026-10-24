from policyengine_us.model_api import *


class mn_employee_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Minnesota employee paid leave contribution"
    documentation = (
        "Employee-side Minnesota Paid Leave premium. The premium is payable "
        "by the employer, which must pay at least half (a small employer "
        "under subd. 5a, at least a quarter of the full rate); employees pay "
        "by wage deduction only the part the employer does not pay (Minn. "
        "Stat. 268B.14, subds. 1, 3 and 5a). This is the largest such part, "
        "half the premium at the full rate, times "
        "state_payroll_premium_deduction_share. The employer premium is not "
        "modeled."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MN
    reference = "https://www.revisor.mn.gov/statutes/cite/268B.14"

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.mn.tax.payroll.paid_leave.employee_rate
        permitted = rate * person("mn_paid_leave_taxable_wages", period)
        return permitted * person("state_payroll_premium_deduction_share", period)
