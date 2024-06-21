from policyengine_us.model_api import *
from policyengine_us.entities import *
from policyengine_us.tools.general import *
from kj_alison_issues.files import * # do we need this one??? #wont hurt?




class new_pw_system_size(Variable):
    value_type = float
    entity = Household
    label = "Size of new system"
    unit = "kW"
    definition_period = YEAR
    reference = ""