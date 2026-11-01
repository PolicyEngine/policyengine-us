from policyengine_us.model_api import *


class dc_taxable_income_indiv(Variable):
    value_type = float
    entity = Person
    label = "DC taxable income (can be negative) when married couple files separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=36",
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=34",
    )
    defined_for = StateCode.DC
    documentation = (
        "Each spouse's DC taxable income when they file separately on the "
        "same return: their DC AGI, with their own capital losses limited as "
        "on a separate return (dc_separate_capital_loss_adjustment), less "
        "their part of the DC deduction."
    )
    adds = ["dc_agi", "dc_separate_capital_loss_adjustment"]
    subtracts = ["dc_deduction_indiv"]
