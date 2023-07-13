from policyengine_us.model_api import *


class mi_exemption_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Michigan household exemption count"
    defined_for = StateCode.MI
    definition_period = YEAR


# todo: exemption calculation
