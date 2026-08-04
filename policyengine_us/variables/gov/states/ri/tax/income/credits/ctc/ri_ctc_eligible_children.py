from policyengine_us.model_api import *


class ri_ctc_eligible_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "Rhode Island Child Tax Credit eligible children"
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = "https://webserver.rilegislature.gov/BillText/BillText26/HouseText26/H7127Aaa.html#:~:text=%E2%80%9CChild%E2%80%9D%20means%20an%20individual%20who%20is%20eighteen%20years%20of%20age%20or%20under"

    adds = ["ri_ctc_eligible_child"]
