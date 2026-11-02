from policyengine_us.model_api import *


class ca_state_supplement_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "California SSI state supplement eligible person"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12150"

    def formula(person, period, parameters):
        # WIC 12150 entitles people who receive SSI or "who but for their
        # income" could, which is SSI eligibility without its income test.
        return person("is_ssi_eligible", period)
