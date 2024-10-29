from policyengine_us.model_api import *


class active_partnership_income(Variable):
    value_type = float
    entity = Person
    label = "Active partnership income"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.partnership_s_corp_income"
