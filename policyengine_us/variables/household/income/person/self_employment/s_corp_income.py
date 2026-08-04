from policyengine_us.model_api import *


class s_corp_income(Variable):
    value_type = float
    entity = Person
    label = "S-corporation income"
    unit = USD
    documentation = "Gross S-corporation income reported through Schedule E."
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.partnership_s_corp_income"
