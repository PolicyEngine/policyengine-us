from policyengine_us.model_api import *


class ca_child_care_work_requirement(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Work Requirement"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        persons = spm_unit.members
        welfare_to_work = persons("ca_child_care_welfare_to_work", period)
        earned = persons("earned_income", period)
        return spm_unit.any(welfare_to_work > 0) & spm_unit.any(earned > 0)
