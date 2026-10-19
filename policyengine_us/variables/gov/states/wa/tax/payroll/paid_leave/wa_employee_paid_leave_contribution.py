from policyengine_us.model_api import *


class wa_employee_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Washington employee paid leave contribution"
    documentation = (
        "Employee-side Washington Paid Family and Medical Leave premium. The "
        "employer collects and remits the premium, may deduct up to the "
        "employee share from wages, and may elect to pay all or any portion "
        "of it (RCW 50A.10.030(3), (7)); this is that permitted share times "
        "state_payroll_premium_deduction_share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=50A.10.030",
        "https://app.leg.wa.gov/WAC/default.aspx?cite=192-510-065",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.tax.payroll.paid_leave
        taxable_wages = person("wa_paid_leave_taxable_wages", period)
        permitted = p.total_rate * (1 - p.employer_share) * taxable_wages
        return permitted * person("state_payroll_premium_deduction_share", period)
