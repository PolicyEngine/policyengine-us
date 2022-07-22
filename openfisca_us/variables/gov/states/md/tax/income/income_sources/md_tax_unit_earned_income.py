from openfisca_us.model_api import *


class md_tax_unit_earned_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD tax unit earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    formula = sum_among_non_dependents("earned_income")
