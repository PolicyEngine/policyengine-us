from policyengine_us.model_api import *


class co_denver_employee_occupational_privilege_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Denver employee occupational privilege tax"
    documentation = (
        "Employee-side Denver occupational privilege tax from explicit "
        "taxable-month inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.denvergov.org/Government/Agencies-Departments-Offices/"
        "Agencies-Departments-Offices-Directory/Department-of-Finance/"
        "Our-Divisions/Treasury/Business-Tax-Information/Business-Tax-FAQ"
    )

    def formula(tax_unit, period, parameters):
        taxable_months = tax_unit.sum(
            tax_unit.members(
                "co_denver_employee_occupational_privilege_tax_months", period
            )
        )
        p = parameters(period).gov.local.co.denver.tax.payroll.occupational_privilege
        return taxable_months * p.employee_amount
