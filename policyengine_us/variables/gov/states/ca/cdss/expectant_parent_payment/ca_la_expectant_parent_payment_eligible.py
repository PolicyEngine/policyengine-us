from policyengine_us.model_api import *


class ca_la_expectant_parent_payment_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=11465.",
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2021/21-123.pdf",
    )
    label = "Eligible for the California expectant parent payment"
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        pregnancy_month = person("current_pregnancy_month", period)
        p = parameters(period).gov.states.ca.cdss.expectant_parent_payment
        eligible_based_on_pregnancy_month = (
            pregnancy_month >= p.pregnancy_month.min
        ) & (pregnancy_month <= p.pregnancy_month.max)
        foster_care_minor_dependent = person("ca_foster_care_minor_dependent", period)
        return foster_care_minor_dependent & eligible_based_on_pregnancy_month
