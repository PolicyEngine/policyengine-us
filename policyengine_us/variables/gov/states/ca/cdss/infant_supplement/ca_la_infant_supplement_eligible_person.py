from policyengine_us.model_api import *


class ca_la_infant_supplement_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=11465.",
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2021/21-123.pdf",
    )
    label = "Eligible for the California infant supplement"
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        foster_eligible = person("ca_foster_care_minor_dependent", period)
        own_children = person("own_children_in_household", period.this_year)
        return foster_eligible & (own_children > 0)
