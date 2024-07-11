from policyengine_us.model_api import *


class la_general_relief_immigration_status_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for the Los Angeles County General Relief based on the immigration status requirements"
    # Person has to be a resident of LA County
    defined_for = "in_la"
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FGR%2FGR%2F42-404_Immigrant_Eligibility_Chart%2F42-404_Immigrant_Eligibility_Chart.htm"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        eligible_person = person(
            "la_general_relief_immigration_status_eligible_person", period
        )
        # To be eligible for General Relief (GR), all applicants/participants must
        # meet the eligibility criteria
        return spm_unit.all(eligible_person)
