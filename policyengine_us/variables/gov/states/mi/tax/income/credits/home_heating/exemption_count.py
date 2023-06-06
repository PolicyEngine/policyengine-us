from policyengine_us.model_api import *


class exemption_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Household exemption count"
    defined_for = StateCode.MI
    unit = people
    definition_period = YEAR
#todo: exemption calculation