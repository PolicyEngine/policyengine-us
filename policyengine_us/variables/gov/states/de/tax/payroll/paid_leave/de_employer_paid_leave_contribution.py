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
    reference = (
        "https://delcode.delaware.gov/title19/c037/#3701",
        "https://regulations.delaware.gov/api/AdminCode/title19/1401/b74cbe9f-04ec-4148-a954-b6907a8ba00a#page=11",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.tax.payroll.paid_leave
        taxable_wages = min_(
            person("payroll_tax_gross_wages", period),
            parameters(period).gov.irs.payroll.social_security.cap,
        )
        return (
            person("de_paid_leave_contribution_rate", period)
            * (1 - p.employee_share)
            * taxable_wages
        )
