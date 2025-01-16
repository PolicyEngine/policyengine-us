from policyengine_us.model_api import *


class farm_rent_income(Variable):
    value_type = float
    entity = Person
    label = "farm rental income"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.farm_rent_income"
