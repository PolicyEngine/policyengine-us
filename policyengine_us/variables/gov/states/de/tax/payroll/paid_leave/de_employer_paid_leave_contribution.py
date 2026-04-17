from policyengine_us.model_api import *


class de_employer_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Delaware employer paid leave contribution"
    documentation = (
        "Employer-side Delaware paid leave contribution, assuming the employer "
        "contributes only the minimum required share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.tax.payroll.paid_leave
        taxable_wages = person("taxable_earnings_for_social_security", period)
        return (
            person("de_paid_leave_contribution_rate", period)
            * (1 - p.employee_share)
            * taxable_wages
        )
