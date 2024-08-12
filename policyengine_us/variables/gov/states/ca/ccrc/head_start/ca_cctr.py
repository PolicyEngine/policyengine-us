from policyengine_us.model_api import *


class ca_cctr(Variable):
    value_type = float
    entity = Person
    label = "Amount of California General Child Care and Development"
    definition_period = YEAR
    defined_for = "ca_cctr_eligible"
