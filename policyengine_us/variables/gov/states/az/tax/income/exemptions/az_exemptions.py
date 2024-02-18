from policyengine_us.model_api import *


class az_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona total exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    adds = [
        "az_aged_exemption",
        "az_blind_exemption",
        "az_parents_grandparents_exemption",
        "az_stillborn_exemption",
    ]
