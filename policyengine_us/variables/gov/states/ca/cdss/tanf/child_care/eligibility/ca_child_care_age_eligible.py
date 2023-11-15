from policyengine_us.model_api import *


class ca_child_care_age_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Child Care Age Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_Overview%2F1210_Overview.htm%23Backgroundbc-3&rhtocid=_3_3_0_2"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.tanf.child_care.eligibility
        person = spm_unit.members
        age = person("age", period)
        is_disabled = person("is_disabled", period)
        disabled_child_eligible = (
            (age <= p.disabled_age_threshold) & (is_disabled)
        )
        younger_child_eligible = age <= p.age_threshold

        return spm_unit.any(disabled_child_eligible | younger_child_eligible)
