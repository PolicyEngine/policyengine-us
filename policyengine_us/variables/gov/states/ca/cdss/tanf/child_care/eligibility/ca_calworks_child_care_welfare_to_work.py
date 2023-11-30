from policyengine_us.model_api import *


class ca_calworks_child_care_welfare_to_work(Variable):
    value_type = float
    entity = Person
    label = "California CalWORKs Welfare to Work"
    unit = "hour"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = [
        "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_Overview%2F1210_Overview.htm%23Backgroundbc-3&rhtocid=_3_3_0_2",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=11322.6.",
    ]
