from policyengine_us.model_api import *


class wv_public_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia public pension subtraction"
    defined_for = StateCode.WV
    unit = USD
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-12/"

    adds = ["wv_public_pension_subtraction_person"]
