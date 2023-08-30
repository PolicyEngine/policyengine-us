from policyengine_us.model_api import *


class de_pre_exclusions_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware adjusted gross income before exclusions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    adds = ["de_additions", "adjusted_gross_income"]
    subtracts = ["de_subtractions"]
