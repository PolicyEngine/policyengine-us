from openfisca_us.model_api import *


class or_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR uncapped refundable tax credits"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables("gov.states.or.tax.income.credits.refundable")
