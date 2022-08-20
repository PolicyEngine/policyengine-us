from openfisca_us.model_api import *


class tanf(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF"
    documentation = (
        "Amount of Temporary Assistance for Needy Families benefit received."
    )
    unit = USD
    defined_for = "is_tanf_eligible"

    def formula(spm_unit, period, parameters):
        tanf_reported = add(spm_unit, period, ["tanf_reported"])
        if tanf_reported.sum() > 0:
            return tanf_reported
        return spm_unit("tanf_amount_if_eligible", period)
