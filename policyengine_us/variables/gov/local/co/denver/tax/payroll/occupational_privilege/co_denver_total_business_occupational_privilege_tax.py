from policyengine_us.model_api import *


class co_denver_total_business_occupational_privilege_tax(Variable):
    value_type = float
    entity = Person
    label = "Total Denver business occupational privilege tax"
    documentation = (
        "Employer-side Denver occupational privilege tax liability from "
        "aggregate taxable employee-month and owner-month inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.denvergov.org/Government/Agencies-Departments-Offices/"
        "Agencies-Departments-Offices-Directory/Department-of-Finance/"
        "Our-Divisions/Treasury/Business-Tax-Information/Business-Tax-FAQ"
    )

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        p = parameters(period).gov.local.co.denver.tax.payroll.occupational_privilege
        employee_months = person(
            "employer_total_co_denver_occupational_privilege_tax_employee_months",
            period,
        )
        owner_months = person(
            "employer_total_co_denver_occupational_privilege_tax_owner_months",
            period,
        )
        return where(
            state_code == StateCode.CO,
            p.employer_amount * (employee_months + owner_months),
            0,
        )
