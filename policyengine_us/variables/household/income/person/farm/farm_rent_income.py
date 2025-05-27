from policyengine_us.model_api import *


class farm_rent_income(Variable):
    value_type = float
    entity = Person
    label = "farm rental income"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.farm_rent_income"


class farm_operations_income(Variable):
    value_type = float
    entity = Person
    label = "farm income"
    unit = USD
    documentation = "Income from active farming operations. Schedule F. Do not include this income in self-employment income."
    definition_period = YEAR
    # Uprate farm operations income using SOI farm income series.
    uprating = "calibration.gov.irs.soi.farm_income"
