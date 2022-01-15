from openfisca_us.model_api import *


class ssi(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Supplemental Security Income amount"
    label = "Supplemental Security Income"
    unit = USD

    def formula(spm_unit, period, parameters):
        # Obtain eligibility.
        eligible = spm_unit("is_ssi_eligible", period)
        # Obtain amount they would receive if they were eligible.
        amount_if_eligible = spm_unit("ssi_amount_if_eligible", period)
        return where(eligible, amount_if_eligible, 0)
