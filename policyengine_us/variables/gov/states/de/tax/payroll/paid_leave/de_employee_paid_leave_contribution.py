from policyengine_us.model_api import *


class de_employee_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Delaware employee paid leave contribution"
    documentation = (
        "Employee-side Delaware paid leave contribution, assuming the employer "
        "withholds the maximum permitted employee share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.tax.payroll.paid_leave
        taxable_wages = person("taxable_earnings_for_social_security", period)
        return (
            person("de_paid_leave_contribution_rate", period)
            * p.employee_share
            * taxable_wages
        )
