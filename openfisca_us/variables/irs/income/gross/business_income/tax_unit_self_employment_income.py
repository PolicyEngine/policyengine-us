from openfisca_us.model_api import *


class tax_unit_self_employment_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit self-employment income"
    unit = USD
    documentation = "Tax unit self-employment income (excludes dependents)."
    definition_period = YEAR

    formula = sum_among_non_dependents("self_employment_income")

tc_e00900 = taxcalc_read_only_variable("tc_e00900", tax_unit_self_employment_income)