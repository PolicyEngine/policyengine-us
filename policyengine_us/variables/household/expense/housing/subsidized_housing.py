from policyengine_us.model_api import *


class subsidized_housing(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Whether household lives in subsidized housing"
    definition_period = YEAR
    reference = "https://liheapch.acf.hhs.gov/tables/FY2016/subsidize.htm#OR"

from policyengine_us.model_api import *


class subsidized_housing(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Household lives in subsidized housing"
    definition_period = YEAR
    reference = "https://liheapch.acf.hhs.gov/tables/FY2015/subsidize.htm"

    def formula(spm_unit, period, parameters):
        housing_assistance = spm_unit("housing_assistance", period)
        return housing_assistance > 0