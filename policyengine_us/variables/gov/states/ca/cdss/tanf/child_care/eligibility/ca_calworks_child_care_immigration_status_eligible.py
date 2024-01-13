from policyengine_us.model_api import *


class ca_calworks_child_care_immigration_status_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "California CalWORKs Child Care SPMUnit immigration status Eligibility"
    )
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_Overview%2F1210_Overview.htm%23Backgroundbc-3&rhtocid=_3_3_0_2"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        head = person("is_tax_unit_head", period)
        immigration_status = person("immigration_status", period)
        status = immigration_status.possible_values
        citizen = immigration_status == status.CITIZEN
        legal_permanent_resident = (
            immigration_status == status.LEGAL_PERMANENT_RESIDENT
        )
        head_eligible = head & (citizen | legal_permanent_resident)
        return spm_unit.any(head_eligible)
