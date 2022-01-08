from openfisca_us.model_api import *


class snap_max_benefit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Maximum benefit for SPM unit, based on the state group and household size."
    label = "SNAP maximum benefit"
    unit = USD

    def formula(spm_unit, period, parameters):
        snap_max_benefits = parameters(period).usda.snap.amount.main
        state_group = spm_unit.household("state_group_str", period)
        household_size = spm_unit.nb_persons()
        return snap_max_benefits[state_group][household_size] * 12
