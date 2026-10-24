from policyengine_us.model_api import *


class me_employee_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Maine employee paid leave contribution"
    documentation = (
        "Employee-side Maine Paid Family and Medical Leave premium. The "
        "employer remits the premium and may deduct up to half of it from "
        "wages (26 M.R.S. s. 850-F(5)); this is that permitted share times "
        "state_payroll_premium_deduction_share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.ME
    reference = "https://legislature.maine.gov/legis/statutes/26/title26sec850-F.html"

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.me.tax.payroll.paid_leave.employee_rate
        permitted = rate * person("me_paid_leave_taxable_wages", period)
        return permitted * person("state_payroll_premium_deduction_share", period)
