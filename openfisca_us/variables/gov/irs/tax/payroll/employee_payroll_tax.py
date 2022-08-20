from openfisca_us.model_api import *


class employee_payroll_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Employee payroll tax"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        PERSON_ELEMENTS = [
            "employee_social_security_tax",
            "employee_medicare_tax",
        ]
        TAX_UNIT_ELEMENTS = ["additional_medicare_tax"]
        return add(tax_unit, period, PERSON_ELEMENTS + TAX_UNIT_ELEMENTS)
