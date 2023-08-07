from policyengine_us.model_api import *


class ca_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=14"
    defined_for = StateCode.MS
    adds = ["adjusted_gross_income", "ms_agi_additions"]
    subtracts = ["ms_agi_subtractions"]
