from policyengine_us.model_api import *


class mt_other_additions(Variable):
    value_type = float
    entity = Person
    label = "Montana other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    documentation = (
        "Montana other additions reported on Form 2, Schedule I, "
        "Line 6 (Other additions), entered as a positive amount."
    )
    reference = "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=23"
