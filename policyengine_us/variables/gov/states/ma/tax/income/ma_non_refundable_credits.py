from policyengine_us.model_api import *


class ma_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA non-refundable credits"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/2021-form-1-massachusetts-resident-income-tax-return/download"
    defined_for = StateCode.MA
    adds = "gov.states.ma.tax.income.credits.non_refundable"
