from policyengine_us.model_api import *


class vt_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont income deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mainelegislature.org/legis/statutes/36/title36sec5126-A.html"
    defined_for = StateCode.VT
