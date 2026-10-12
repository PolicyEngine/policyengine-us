from policyengine_us.model_api import *


class wi_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wisconsin child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WI
    reference = "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=155"
    adds = ["wi_shares"]
