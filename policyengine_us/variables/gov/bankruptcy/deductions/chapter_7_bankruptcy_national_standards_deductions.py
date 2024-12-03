from policyengine_us.model_api import *


class chapter_7_bankruptcy_national_standards_deductions(Variable):
    value_type = bool
    entity = SPMUnit
    label = "National standards deduction"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=2"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.bankruptcy.national_standards
        size = spm_unit("spm_unit_size", period)
        capped_people = min_(size, 4).astype(int)
        additional_people = size - capped_people
        base = p.food_clothing_and_others.main[capped_people]
        additional_amount = p.food_clothing_and_others.additional * additional_people
        food_clothing_and_others_allowance = base + additional_amount
        
        age = spm_unit.members("age",period)
        out_of_pocket_health_care_allowance = p.out_of_pocket_health_care.amount.calc(age)
        return food_clothing_and_others_allowance + out_of_pocket_health_care_allowance
    