from policyengine_us.model_api import *


class ca_calworks_child_care_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "California CalWORKs Child Care immigration status Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_Overview%2F1210_Overview.htm%23Backgroundbc-3&rhtocid=_3_3_0_2"

    def formula(person, period, parameters):
        immigration_status = person("immigration_status", period)
        p = parameters(
            period
        ).gov.states.ca.cdss.tanf.child_care.eligibility.immigration_status

        immigration_status_str = immigration_status.decode_to_str()

        return np.isin(
            immigration_status_str,
            p.eligible_statuses,
        )
