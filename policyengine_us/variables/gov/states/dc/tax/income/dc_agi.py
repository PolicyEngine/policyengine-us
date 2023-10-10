from policyengine_us.model_api import *


class dc_agi(Variable):
    value_type = float
    entity = Person
    label = "DC AGI (adjusted gross income) for each person in tax unit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=36"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=34"
    )
    defined_for = StateCode.DC
    adds = ["adjusted_gross_income_person", "dc_income_additions"]
    subtracts = ["dc_income_subtractions"]
