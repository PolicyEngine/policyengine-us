from openfisca_us.model_api import *


class health_savings_account_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Health savings account ALD"
    unit = USD
    documentation = "Above-the-line deduction from gross income for health savings account expenses."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/223"
