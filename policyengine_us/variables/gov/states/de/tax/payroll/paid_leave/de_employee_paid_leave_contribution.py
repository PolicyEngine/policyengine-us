from policyengine_us.model_api import *


class de_employee_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Delaware employee paid leave contribution"
    documentation = (
        "Employee-side Delaware Paid Leave contribution. The employer remits "
        "the contribution and may deduct up to half of it from wages "
        "(19 Del. C. s. 3705(d)-(g)); this is that permitted share times "
        "state_payroll_premium_deduction_share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.DE
    reference = "https://delcode.delaware.gov/title19/c037/index.html"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.tax.payroll.paid_leave
        taxable_wages = person("taxable_earnings_for_social_security", period)
        permitted = (
            person("de_paid_leave_contribution_rate", period)
            * p.employee_share
            * taxable_wages
        )
        return permitted * person("state_payroll_premium_deduction_share", period)
