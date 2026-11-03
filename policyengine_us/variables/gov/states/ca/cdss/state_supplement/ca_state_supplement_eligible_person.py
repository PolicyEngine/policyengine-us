from policyengine_us.model_api import *


class ca_state_supplement_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "California SSI state supplement eligible person"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12150"

    def formula(person, period, parameters):
        # is_ssi_eligible has no income test, so a person qualifies only when
        # their income leaves a supplement to pay.
        return person("ca_state_supplement_person", period) > 0
