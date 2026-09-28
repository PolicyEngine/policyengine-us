from policyengine_us.model_api import *


class ca_care_categorically_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Eligible for California CARE program by virtue of participation in a qualifying program"
    documentation = "Eligible for California Alternate Rates for Energy"
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.1"
    defined_for = StateCode.CA

    def formula(household, period, parameters):
        p = parameters(period).gov.states.ca.cpuc.care.eligibility
        is_on_tribal_land = household("is_on_tribal_land", period)
        general_programs = add(household, period, p.categorical)
        tribal_programs = add(household, period, p.tribal_categorical)
        # Tribal households qualify through every general program as well as
        # the tribal-only additions.
        return (general_programs > 0) | (is_on_tribal_land & (tribal_programs > 0))
