from policyengine_us.model_api import *


class farm_rent_income(Variable):
    value_type = float
    entity = Person
    label = "farm rental income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/1402"
    uprating = "calibration.gov.irs.soi.farm_rent_income"
