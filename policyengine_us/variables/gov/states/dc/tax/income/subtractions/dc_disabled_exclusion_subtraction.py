from policyengine_us.model_api import *


class dc_disabled_exclusion_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC disabled exclusion subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=63"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2021_D-2440.pdf"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=55"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-2440.pdf"
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, paramters):
        return 0
