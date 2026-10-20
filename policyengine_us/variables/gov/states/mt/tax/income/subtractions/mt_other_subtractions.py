from policyengine_us.model_api import *


class mt_other_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Montana other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    documentation = (
        "Montana other subtractions reported on Form 2, Subtractions Schedule, "
        "line 23 (Other subtractions), entered as a positive amount. "
        "Do not include interest exemptions, tuition subtractions, old age/disability exclusions, "
        "federal deductions, or state tax refunds, which PolicyEngine computes separately."
    )
    reference = "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=21"
