from policyengine_us.model_api import *


class passive_s_corp_loss(Variable):
    value_type = float
    entity = Person
    label = "Passive S-corp loss"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.partnership_s_corp_income"
