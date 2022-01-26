from openfisca_us.model_api import *


class spm_unit_taxes(Variable):
    value_type = float
    entity = SPMUnit
    label = "Taxes"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        SPMU_COMPONENTS = [
            "spm_unit_fica",
            "spm_unit_federal_tax",
            "spm_unit_state_tax",
        ]
        return add(spm_unit, period, SPMU_COMPONENTS)
