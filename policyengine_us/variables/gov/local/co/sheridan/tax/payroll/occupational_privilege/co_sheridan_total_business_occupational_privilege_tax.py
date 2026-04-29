from policyengine_us.model_api import *


class co_sheridan_total_business_occupational_privilege_tax(Variable):
    value_type = float
    entity = Person
    label = "Total Sheridan business occupational privilege tax"
    documentation = (
        "Employer-side Sheridan occupational privilege tax liability from "
        "aggregate taxable employee-month inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = "https://www.ci.sheridan.co.us/288/Occupational-Privilege-Tax"

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        p = parameters(period).gov.local.co.sheridan.tax.payroll.occupational_privilege
        employee_months = person(
            "employer_total_co_sheridan_occupational_privilege_tax_employee_months",
            period,
        )
        return where(
            state_code == StateCode.CO,
            p.employer_amount * employee_months,
            0,
        )
