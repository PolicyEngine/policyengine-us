from policyengine_us.model_api import *


class ca_calworks_child_care_meets_work_requirement(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets CalWORKs Child Care Work Requirement"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_Overview%2F1210_Overview.htm%23Backgroundbc-3&rhtocid=_3_3_0_2"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        welfare_to_work = person("ca_child_care_welfare_to_work", period)
        earned = person("earned_income", period)
        return spm_unit.any(welfare_to_work > 0) | spm_unit.any(earned > 0)
