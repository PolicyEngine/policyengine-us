from openfisca_us.model_api import *


class social_security_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Social security taxes"
    unit = "currency-USD"
    documentation = "Total employee-side social security taxes"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        employee_payroll_tax = 0.5 * tax_unit("ptax_was", period)
        self_employed_tax = tax_unit("c03260", period)
        unreported_payroll_tax = aggr(tax_unit, period, ["e09800"])
        excess_payroll_tax_withheld = aggr(tax_unit, period, ["e11200"])
        return (
            employee_payroll_tax
            + self_employed_tax
            + unreported_payroll_tax
            - excess_payroll_tax_withheld
        )
