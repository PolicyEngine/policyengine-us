from policyengine_us.model_api import *


class farm_operations_income(Variable):
    value_type = float
    entity = Person
    label = "farm operations income"
    unit = USD
    documentation = "Income from active farming operations. Schedule F. Do not include this income in self-employment income."
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.farm_income"
