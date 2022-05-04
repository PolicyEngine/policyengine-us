from openfisca_us.model_api import *


class tax_unit_alimony_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit alimony income"
    unit = USD
    documentation = "Tax unit alimony income."
    definition_period = YEAR

    formula = sum_among_non_dependents("alimony_income")

tc_e00800 = taxcalc_read_only_variable("tc_e00800", tax_unit_alimony_income)