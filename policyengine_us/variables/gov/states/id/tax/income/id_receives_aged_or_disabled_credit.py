from policyengine_us.model_api import *


class id_receives_aged_or_disabled_credit(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Filer receives the Idaho aged or disabled credit over the deduction"
    )
    definition_period = YEAR
    defined_for = StateCode.ID
    default_value = True
