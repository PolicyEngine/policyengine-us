from openfisca_us.model_api import *


class tax_unit_farm_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit farm income"
    unit = USD
    documentation = "Tax unit farm income (excludes dependents)."
    definition_period = YEAR

    formula = sum_among_non_dependents("farm_income")

tc_e02100 = taxcalc_read_only_variable("tc_e02100", tax_unit_farm_income)