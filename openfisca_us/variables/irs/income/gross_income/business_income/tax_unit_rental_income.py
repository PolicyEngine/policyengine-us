from openfisca_us.model_api import *


class tax_unit_rental_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit rental income"
    unit = USD
    documentation = "Tax unit rental, royalty, etc. income."
    definition_period = YEAR

    formula = sum_among_non_dependents("rental_income")

tc_e02000 = taxcalc_read_only_variable("tc_e02000", tax_unit_rental_income)