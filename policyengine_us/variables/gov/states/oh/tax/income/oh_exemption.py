from policyengine_us.model_api import *


class oh_exemption(Variable):
    #for reference
    value_type = float
    entity = TaxUnit
    label = "Ohio exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH
