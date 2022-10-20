from policyengine_us.model_api import *


class taxable_income_deductions_if_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Deductions if itemizing"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables("gov.irs.deductions.deductions_if_itemizing")
