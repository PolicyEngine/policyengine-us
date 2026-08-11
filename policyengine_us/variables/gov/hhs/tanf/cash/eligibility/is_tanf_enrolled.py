from policyengine_us.model_api import *


class is_tanf_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Enrolled in TANF"
    documentation = (
        "Whether the family is currently enrolled in the Temporary "
        "Assistance for Needy Families program. Defaults to reported TANF "
        "receipt (receives_tanf); set directly to override."
    )

    def formula(spm_unit, period, parameters):
        return spm_unit("receives_tanf", period)
