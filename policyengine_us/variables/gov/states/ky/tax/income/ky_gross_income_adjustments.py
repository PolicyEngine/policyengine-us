from policyengine_us.model_api import *


class ky_gross_income_adjustments(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky gross income adjustments "
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    adds = "gov.states.ky.tax.income.gross_income_adjustments.sources"