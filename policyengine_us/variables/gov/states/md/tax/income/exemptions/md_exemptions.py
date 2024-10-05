from policyengine_us.model_api import *


class md_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    adds = ["md_total_personal_exemptions", "md_aged_blind_exemptions"]
