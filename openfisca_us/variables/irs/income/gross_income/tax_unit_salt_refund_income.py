from openfisca_us.model_api import *


class tax_unit_salt_refund_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit SALT refund income"
    unit = USD
    documentation = "Tax unit state and local tax refund income."
    definition_period = YEAR

    formula = sum_among_non_dependents("salt_refund_income")

tc_e00700 = taxcalc_read_only_variable("tc_e00700", tax_unit_salt_refund_income)