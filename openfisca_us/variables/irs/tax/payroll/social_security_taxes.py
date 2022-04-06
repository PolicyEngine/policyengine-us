from openfisca_us.model_api import *


class social_security_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Social security taxes"
    unit = "currency-USD"
    documentation = "Total employee-side social security taxes"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        PERSON_VARIABLES = [
            "employee_social_security_tax",
            "employee_medicare_tax",
            "e09800",  # Unreported payroll tax.
        ]
        PERSON_VARIABLES_SUBTRACT = ["e11200"]  # Excess payroll tax withheld.
        TAX_UNIT_VARIABLES = ["c03260"]  # Self-employed tax.
        return (
            aggr(tax_unit, period, PERSON_VARIABLES)
            + add(tax_unit, period, TAX_UNIT_VARIABLES)
            - aggr(tax_unit, period, PERSON_VARIABLES_SUBTRACT)
        )
