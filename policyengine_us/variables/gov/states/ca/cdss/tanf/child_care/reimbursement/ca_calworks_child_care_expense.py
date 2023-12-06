from policyengine_us.model_api import *


class ca_calworks_child_care_expense(Variable):
    value_type = float
    entity = Person
    label = "California CalWORKs monthly child care expense"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
