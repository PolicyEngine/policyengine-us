from openfisca_us.model_api import *


class taxable_income_deductions_if_not_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable income deductions if not itemizing"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/63#b"

    formula = sum_of_variables("irs.deductions.deductions_if_not_itemizing")