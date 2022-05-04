from openfisca_us.model_api import *


class tax_unit_employment_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit employment income"
    unit = USD
    documentation = "Employment income for the tax unit (excludes dependent income)."
    definition_period = YEAR

    formula = sum_among_non_dependents("employment_income")

tc_e00200 = taxcalc_read_only_variable("tc_e00200", tax_unit_employment_income)
