from policyengine_us.model_api import *


class ca_la_expectant_parent_payment(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=11465.",
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2021/21-123.pdf",
        "https://cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2026/26-44.pdf#page=5",
    )
    label = "California expectant parent payment"
    defined_for = "ca_la_expectant_parent_payment_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.cdss.expectant_parent_payment.amount
        is_in_group_home = person("is_in_foster_care_group_home", period)
        return where(is_in_group_home, p.group_home, p.base)
