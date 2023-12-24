from policyengine_us.model_api import *


class ca_fytc_care(Variable):
    value_type = bool
    entity = Person
    label = "Foster Care"
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-3514.pdf#page=4"

