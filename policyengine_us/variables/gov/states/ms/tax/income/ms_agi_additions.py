from policyengine_us.model_api import *


class ca_agi_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MS AGI additions to federal AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf"
    defined_for = StateCode.MS
