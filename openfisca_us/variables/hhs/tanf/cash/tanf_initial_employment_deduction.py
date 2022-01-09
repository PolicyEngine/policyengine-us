from openfisca_us.model_api import *


class tanf_initial_employment_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF IED (Initial Employment Deduction)"
    documentation = "The amount deducted from the countable earnings of a TANF application when calculating initial eligibility."
    unit = USD

    def formula(spm_unit, period, parameters):
        family_size = spm_unit.nb_persons().astype(str)
        state = spm_unit.household("state_code_str", period)
        ied = parameters(period).hhs.tanf.cash.initial_employment_deduction
        return ied[state][family_size] * 12
