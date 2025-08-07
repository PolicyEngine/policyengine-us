from policyengine_us.model_api import *


class alimony_income(Variable):
    value_type = float
    entity = Person
    label = "Alimony income"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.self_employment_income"
