from policyengine_us.model_api import *


class co_glendale_employee_occupational_privilege_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Glendale employee occupational privilege tax"
    documentation = (
        "Employee-side Glendale occupational privilege tax from explicit "
        "taxable-month inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = "https://www.glendale.co.us/355/Occupational-Privilege-Tax"

    def formula(tax_unit, period, parameters):
        taxable_months = tax_unit.sum(
            tax_unit.members(
                "co_glendale_employee_occupational_privilege_tax_months", period
            )
        )
        p = parameters(period).gov.local.co.glendale.tax.payroll.occupational_privilege
        return taxable_months * p.employee_amount
