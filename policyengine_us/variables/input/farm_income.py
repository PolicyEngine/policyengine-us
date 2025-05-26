from policyengine_us.model_api import *


class farm_income(Variable):
    value_type = float
    entity = Person
    label = "farm income"
    unit = USD
    documentation = "Income averaging for farmers and fishermen. Schedule J. Seperate from QBI and self-employment income."
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.farm_income"
