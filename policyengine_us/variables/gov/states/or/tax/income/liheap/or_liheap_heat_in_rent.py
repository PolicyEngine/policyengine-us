from policyengine_us.model_api import *


class heat_in_rent(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Household's heat is included in rent"
    definition_period = YEAR
    reference = "https://liheapch.acf.hhs.gov/tables/FY2016/subsidize.htm#OR"
