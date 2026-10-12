from policyengine_us.model_api import *


class partnership_income(Variable):
    value_type = float
    entity = Person
    label = "partnership income"
    unit = USD
    documentation = "Gross partnership income reported through Schedule E."
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.partnership_s_corp_income"
