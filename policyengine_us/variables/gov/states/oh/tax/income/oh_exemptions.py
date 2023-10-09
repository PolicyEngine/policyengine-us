from policyengine_us.model_api import *


class oh_exemptions(Variable):
    # for reference
    value_type = float
    entity = TaxUnit
    label = "Ohio exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH
