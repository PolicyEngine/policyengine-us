from policyengine_us.model_api import *


class partnership_s_corp_income(Variable):
    value_type = float
    entity = Person
    label = "Total S-corp income/loss"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.partnership_s_corp_income"
