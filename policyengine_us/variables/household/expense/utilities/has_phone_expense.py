from policyengine_us.model_api import *


class has_phone_expense(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Has phone costs"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):  # pragma: no cover
        return add(spm_unit, period, ["phone_expense"]) > 0
