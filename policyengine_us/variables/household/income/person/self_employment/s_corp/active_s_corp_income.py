from policyengine_us.model_api import *


class active_s_corp_income(Variable):
    value_type = float
    entity = Person
    label = "Active S-corp income"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.partnership_s_corp_income"
