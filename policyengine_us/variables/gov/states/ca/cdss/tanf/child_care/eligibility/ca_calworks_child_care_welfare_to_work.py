from policyengine_us.model_api import *


class ca_calworks_child_care_welfare_to_work(Variable):
    value_type = float
    entity = Person
    label = "California CalWORKs Welfare to Work"
    unit = "hour"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = [
        "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/child-care/overview.html",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=11322.6.",
    ]
