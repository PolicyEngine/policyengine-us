from openfisca_us.model_api import *


class tax_unit_partnership_s_corp_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit partnership/S-corp income"
    unit = USD
    documentation = (
        "Combined partnership/S-corporation income for the tax unit."
    )
    definition_period = YEAR

    formula = sum_of_variables(["partnership_s_corp_income"])
