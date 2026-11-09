from policyengine_us.model_api import *


class mt_federal_itemized_personal_property_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Personal property taxes included in the federal SALT deduction for Montana"
    unit = USD
    documentation = (
        "Actual personal property tax component reported on federal Schedule A "
        "line 5c, used to isolate the state income tax component of the capped "
        "Schedule A line 5e amount. Default zero because the federal model "
        "does not separately model personal property taxes. This input does "
        "not itself increase the federal SALT deduction."
    )
    definition_period = YEAR
    reference = "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=22"
    defined_for = StateCode.MT
