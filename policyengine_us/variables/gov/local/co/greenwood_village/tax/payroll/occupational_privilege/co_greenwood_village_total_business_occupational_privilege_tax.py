from policyengine_us.model_api import *


class co_greenwood_village_total_business_occupational_privilege_tax(Variable):
    value_type = float
    entity = Person
    label = "Total Greenwood Village business occupational privilege tax"
    documentation = (
        "Employer-side Greenwood Village occupational privilege tax liability "
        "from aggregate taxable employee-month and owner-month inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = "https://www.greenwoodvillage.com/1220/Occupational-Privilege-Tax-OPT"

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        p = parameters(
            period
        ).gov.local.co.greenwood_village.tax.payroll.occupational_privilege
        employee_months = person(
            "employer_total_co_greenwood_village_occupational_privilege_tax_employee_months",
            period,
        )
        owner_months = person(
            "employer_total_co_greenwood_village_occupational_privilege_tax_owner_months",
            period,
        )
        return where(
            state_code == StateCode.CO,
            p.employer_amount * (employee_months + owner_months),
            0,
        )
