from openfisca_us.model_api import *


class has_telephone_expense(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Has telephone costs"
    documentation = "Whether the household has telephone (or equivalent) costs"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        return add(spm_unit, period, ["telephone_expense"]) > 0
