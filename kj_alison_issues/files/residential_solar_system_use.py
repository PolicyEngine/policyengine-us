from ... policyengine_us.model_api import *
from ... policyengine_us.entities import *
from ... policyengine_us.tools.general import *
from ... kj_alison_issues.files import * # do we need this one??? #wont hurt?




class residential_solar_energy_systems_equipment_incentives(Variable):
    value_type = float
    entity = Household
    label = "Incentives by region: NY"
    documentation = ""
    unit = USD
    definition_period = YEAR 
    reference = "https://portal.nyserda.ny.gov/servlet/servlet.FileDownload?file=00P8z000001BIuBEAW"
