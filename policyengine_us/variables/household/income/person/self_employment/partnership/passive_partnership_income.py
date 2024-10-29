from policyengine_us.model_api import *


class passive_partnership_income(Variable):
    value_type = float
    entity = Person
    label = "Passive partnership income"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.partnership_s_corp_income"
