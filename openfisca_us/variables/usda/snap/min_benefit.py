from openfisca_us.model_api import *


class snap_min_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP minimum benefit"
    unit = "currency-USD"
    documentation = "The SNAP entitlement that would be required to meet the minimum benefit requirement."
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        under_three_members = spm_unit.nb_persons() <= 2
        single_person_max = parameters(period).usda.snap.amount.main[
            spm_unit.household("state_group_str", period)
        ]["1"]
        return under_three_members * single_person_max * 0.08
