from policyengine_us.model_api import *


class chapter_7_bankruptcy_out_of_pocket_health_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Chapter 7 Bankruptcy national standard of Out-of-pocket health care deduction"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=2"
    documentation = "Line 7 in form 122A-2"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.bankruptcy.national_standards.out_of_pocket_health_care.amount

        age = spm_unit.members("monthly_age", period)
        out_of_pocket_health_care_allowance = p.calc(age)

        return spm_unit.sum(out_of_pocket_health_care_allowance)
