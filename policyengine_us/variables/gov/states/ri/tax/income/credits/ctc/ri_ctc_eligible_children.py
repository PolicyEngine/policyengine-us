from policyengine_us.model_api import *


class ri_ctc_eligible_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "Rhode Island Child Tax Credit eligible children"
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = "https://webserver.rilegislature.gov/BillText/BillText26/HouseText26/H7127Aaa.html#bookmark6"

    adds = ["ri_ctc_eligible_child"]
