from policyengine_us.model_api import *


class wi_shares(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Wisconsin Shares child care subsidy"
    definition_period = MONTH
    defined_for = "wi_shares_eligible"
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=155",
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/III/155",
    )
    adds = ["wi_shares_child_subsidy"]
