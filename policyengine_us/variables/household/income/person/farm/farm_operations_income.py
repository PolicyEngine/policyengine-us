from policyengine_us.model_api import *


class farm_operations_income(Variable):
    value_type = float
    entity = Person
    label = "farm operations income"
    unit = USD
    documentation = "Income from active farming operations. Schedule F. Do not include this income in self-employment income."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#c_3_A"
    uprating = "calibration.gov.irs.soi.farm_income"
