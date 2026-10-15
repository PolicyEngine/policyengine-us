from policyengine_us.model_api import *


class in_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana refundable income tax credits"
    unit = USD
    definition_period = YEAR
    reference = "https://iga.in.gov/laws/2021/ic/titles/6#6-3.1"
    defined_for = StateCode.IN
    adds = "gov.states.in.tax.income.credits.refundable"
