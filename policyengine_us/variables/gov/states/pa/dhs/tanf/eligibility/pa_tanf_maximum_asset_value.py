from policyengine_us.model_api import *


class pa_tanf_maximum_assets(Variable):
    value_type = bool
    entity = SPMUnit
    label = "PA TANF maximum assets"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA

    def formula(spm_unit, period, parameters):
        maximum_assets = parameters(
            period
        ).gov.states.pa.dhs.tanf.maximum_asset_value
        total_assets = spm_unit("spm_unit_assets", period)
        return total_assets < maximum_assets
