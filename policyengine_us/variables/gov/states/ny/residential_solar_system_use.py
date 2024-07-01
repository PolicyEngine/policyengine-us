from policyengine_us.model_api import *




class new_pw_system_size(Variable):
    value_type = float
    entity = Household
    label = "Size of new system"
    unit = "kW"
    definition_period = YEAR
    reference = ""