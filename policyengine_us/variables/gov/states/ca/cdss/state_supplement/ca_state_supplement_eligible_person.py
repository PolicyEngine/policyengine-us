from policyengine_us.model_api import *


class ca_state_supplement_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Receives the California state supplement"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12150"

    def formula(person, period, parameters):
        # True only for a person paid the supplement. is_ssi_eligible has no
        # income test, so income that leaves no supplement makes this false, and
        # so does not taking up SSI, because the amount requires take-up.
        return person("ca_state_supplement_person", period) > 0
