from policyengine_us.model_api import *


class taxable_income_deductions_if_not_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Deductions if not itemizing"
    unit = USD
    definition_period = YEAR

    adds = "gov.irs.deductions.deductions_if_not_itemizing"
