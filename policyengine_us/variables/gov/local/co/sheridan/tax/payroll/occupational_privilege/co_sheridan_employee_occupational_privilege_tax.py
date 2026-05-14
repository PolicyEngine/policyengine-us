from policyengine_us.model_api import *


class co_sheridan_employee_occupational_privilege_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Sheridan employee occupational privilege tax"
    documentation = (
        "Employee-side Sheridan occupational privilege tax from explicit "
        "taxable-month inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = "https://www.ci.sheridan.co.us/288/Occupational-Privilege-Tax"

    def formula(tax_unit, period, parameters):
        taxable_months = tax_unit.sum(
            tax_unit.members(
                "co_sheridan_employee_occupational_privilege_tax_months", period
            )
        )
        p = parameters(period).gov.local.co.sheridan.tax.payroll.occupational_privilege
        return taxable_months * p.employee_amount
