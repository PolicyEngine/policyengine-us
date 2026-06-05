from policyengine_us.model_api import *


class oh_homestead_exemption_qualifying_surviving_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Ohio homestead exemption qualifying surviving spouse"
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-323.152"
