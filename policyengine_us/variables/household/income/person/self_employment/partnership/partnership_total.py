from policyengine_us.model_api import *


class partnership_total(Variable):
    value_type = float
    entity = Person
    label = "Total partnership income/loss"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.partnership_s_corp_income"
