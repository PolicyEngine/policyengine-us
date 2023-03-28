from policyengine_us.model_api import *


class me_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine income exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mainelegislature.org/legis/statutes/36/title36sec5126-A.html"
    defined_for = StateCode.ME

    adds = ["me_personal_exemption_deduction"]
