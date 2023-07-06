from policyengine_us.model_api import *


class wv_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-4E/"
    defined_for = StateCode.WV
