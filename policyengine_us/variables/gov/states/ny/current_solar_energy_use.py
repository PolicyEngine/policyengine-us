from policyengine_us.model_api import *
from policyengine_us.entities import *
from policyengine_us.tools.general import *
from kj_alison_issues.files import * 



class current_solar_energy_use(Variable):
    value_type = float
    entity = Household
    label = "Past year or projected year home energy use in annual kilowatt hours"
    unit = "kWh/year"
    definition_period = YEAR
    reference = ""