from policyengine_us.model_api import *


class tanf(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF"
    documentation = (
        "Value of Temporary Assistance for Needy Families benefit received."
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        eligible = spm_unit("is_tanf_eligible", period)
        federal_amount_if_eligible = spm_unit("tanf_amount_if_eligible", period)
        p = parameters(period).gov.hhs.tanf
        return where(eligible, federal_amount_if_eligible, 0) + p.state_programs

