from policyengine_us.model_api import *


class ca_calworks_child_care_meets_work_requirement(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets CalWORKs Child Care Work Requirement"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/child-care/overview.html"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        welfare_to_work = person("ca_calworks_child_care_welfare_to_work", period)
        earned = person("earned_income", period)
        eligible_person = (welfare_to_work + earned) > 0
        return spm_unit.any(eligible_person)
