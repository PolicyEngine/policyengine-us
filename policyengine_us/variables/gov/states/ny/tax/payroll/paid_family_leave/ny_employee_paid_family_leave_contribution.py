from policyengine_us.model_api import *


class ny_employee_paid_family_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "New York employee paid family leave contribution"
    documentation = (
        "Employee-side New York Paid Family Leave contribution. The employer "
        "is authorized, not required, to collect it by payroll deduction up "
        "to the rate and annual maximum the Department of Financial Services "
        "sets (Workers' Compensation Law s. 209(3)(b), (4)); this is that "
        "permitted amount times state_payroll_premium_deduction_share. The "
        "employer's cost of coverage is not modeled."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NY
    reference = "https://www.nysenate.gov/legislation/laws/WKC/209"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.tax.payroll.paid_family_leave
        uncapped = p.employee_rate * person(
            "ny_paid_family_leave_taxable_wages", period
        )
        permitted = min_(uncapped, p.annual_max_contribution)
        return permitted * person("state_payroll_premium_deduction_share", period)
