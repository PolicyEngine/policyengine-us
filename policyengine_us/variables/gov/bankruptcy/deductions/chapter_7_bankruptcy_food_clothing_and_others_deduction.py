from policyengine_us.model_api import *


class chapter_7_bankruptcy_food_clothing_and_others_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Chapter 7 Bankruptcy national standards of food, clothing and other items deduction"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=2"
    documentation = "Line 6 in form 122A-2"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.bankruptcy.national_standards.food_clothing_and_others
        size = spm_unit("spm_unit_size", period)
        capped_people = min_(size, 4).astype(int)
        additional_people = size - capped_people
        base = p.main[capped_people]
        additional_amount = p.additional * additional_people

        return base + additional_amount
