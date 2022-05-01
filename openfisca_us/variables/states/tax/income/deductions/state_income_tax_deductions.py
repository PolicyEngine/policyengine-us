from openfisca_us.model_api import *


class state_income_tax_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax deductions"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(
        [
            "state_income_tax_payroll_tax_deduction",
            "state_income_tax_rental_deduction",
        ]
    )
