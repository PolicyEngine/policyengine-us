from policyengine_us.model_api import *


class co_greenwood_village_employee_occupational_privilege_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Greenwood Village employee occupational privilege tax"
    documentation = (
        "Employee-side Greenwood Village occupational privilege tax from "
        "explicit taxable-month inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = "https://greenwoodvillage.com/files/newsletter2010/April2010/TakeNote.pdf#page=18"

    def formula(tax_unit, period, parameters):
        taxable_months = tax_unit.sum(
            tax_unit.members(
                "co_greenwood_village_employee_occupational_privilege_tax_months",
                period,
            )
        )
        p = parameters(
            period
        ).gov.local.co.greenwood_village.tax.payroll.occupational_privilege
        return taxable_months * p.employee_amount
