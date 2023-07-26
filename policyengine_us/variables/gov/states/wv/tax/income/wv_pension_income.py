from policyengine_us.model_api import *


class wv_pension_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia public pension income"
    unit = USD
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-12/"
    defined_for = StateCode.WV
