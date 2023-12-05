from policyengine_us.model_api import *


class ky_personal_tax_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky personal tax credits"
    unit = USD
    reference = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500#page=3"  # (3) (a)
    definition_period = YEAR
    defined_for = StateCode.KY

    adds = [
        "ky_blind_personal_tax_credits",
        "ky_aged_personal_tax_credits",
        "ky_military_personal_tax_credits",
    ]
