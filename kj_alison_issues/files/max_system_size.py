from ... policyengine_us.model_api import *
from ... policyengine_us.entities import *
from ... policyengine_us.tools.general import *
from ... kj_alison_issues.files import * # do we need this one??? #wont hurt?



class residential_solar_energy_systems_equipment_max_size_li(Variable):
    value_type = float
    entity = Household #is this right?
    label = "max system size per year"
    documentation = ""
    unit = kw
    definition_period = YEAR #where am I importing this from???
    reference = "https://portal.nyserda.ny.gov/servlet/servlet.FileDownload?file=00P8z000001BIuBEAW"


class residential_solar_energy_systems_equipment_max_size_other(Variable):
    value_type = float
    entity = TaxUnit
    label = "ConEd Upstate solar energy systems equipment incentives"
    documentation = ""
    unit = USD
    definition_period = YEAR
    reference = "https://portal.nyserda.ny.gov/servlet/servlet.FileDownload?file=00P8z000001BIuBEAW"