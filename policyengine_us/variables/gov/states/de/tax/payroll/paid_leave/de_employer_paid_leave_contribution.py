from policyengine_us.model_api import *


class de_employer_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Delaware employer paid leave contribution"
    documentation = (
        "Employer-side Delaware Paid Leave contribution: the half the "
        "employer may not deduct, plus the part of the permitted employee "
        "half it does not deduct, for which it remains liable "
        "(19 Del. C. s. 3705(g))."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.DE
    reference = "https://delcode.delaware.gov/title19/c037/index.html"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.tax.payroll.paid_leave
        taxable_wages = person("taxable_earnings_for_social_security", period)
        deducted = p.employee_share * person(
            "state_payroll_premium_deduction_share", period
        )
        return (
            person("de_paid_leave_contribution_rate", period)
            * (1 - deducted)
            * taxable_wages
        )
