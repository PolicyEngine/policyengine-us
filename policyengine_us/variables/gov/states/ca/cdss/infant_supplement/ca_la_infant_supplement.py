from policyengine_us.model_api import *


class ca_la_infant_supplement(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=11465.",
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2021/21-123.pdf",
    )
    label = "California infant supplement"
    defined_for = StateCode.CA

    def formula(household, period, parameters):
        p = parameters(period).gov.states.ca.cdss.infant_supplement
        person = household.members
        is_in_group_home = household.any(person("is_in_foster_care_group_home", period))
        base_amount = where(is_in_group_home, p.amount.group_home, p.amount.base)
        children = add(household, period, ["is_child"])
        eligible_person = person("ca_la_infant_supplement_eligible_person", period)
        eligible_person_present = household.any(eligible_person)
        return base_amount * children * eligible_person_present
