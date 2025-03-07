from policyengine_us.model_api import *




class ny_sun_new_pw_system_size(Variable):
    value_type = float
    entity = Household
    label = "Size of new system"
    unit = "kW"
    definition_period = YEAR
    reference = "https://portal.nyserda.ny.gov/servlet/servlet.FileDownload?file=00P8z000001BIuBEAW"
