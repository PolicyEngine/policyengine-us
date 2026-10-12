from policyengine_us.model_api import *


class ok_ssp_has_essential_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Oklahoma SSP recipient has an essential spouse"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-15-1-5"
