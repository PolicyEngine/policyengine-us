from openfisca_us.model_api import *


class spm_unit_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit's federal poverty guideline"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        n = spm_unit.nb_persons()
        state_group = spm_unit.household("state_group_str", period)
        p_fpg = parameters(period).hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        return p1 + pn * (n - 1)
