from openfisca_us.model_api import *


class tax_unit_ordinary_dividend_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit ordinary dividend income"
    unit = USD
    documentation = "Tax unit ordinary dividend income (excludes dependents)."
    definition_period = YEAR

    formula = sum_among_non_dependents("ordinary_dividend_income")

tc_e00600 = taxcalc_read_only_variable("tc_e00600", tax_unit_ordinary_dividend_income)