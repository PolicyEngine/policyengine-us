from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.demographic.spm_unit import *

# add new variable for enum tier


class ccdf_initial_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):
        # Get state and poverty ratio for SPM unit.
        state = spm_unit("spm_unit_state", period)
        poverty_ratio = spm_unit("poverty_ratio", period)
        assets = spm_unit("spm_unit_assets", period)
        # Get parameters.
        p_ccdf_elig = parameters(period).benefit.CCDF.eligibility
        p_income_limit = p_ccdf_elig.initial_income[state]
        p_asset_limit = p_ccdf_elig.assets[state]
        # Determine eligibility by income (% poverty) and assets.
        income_elig = poverty_ratio <= p_income_limit
        assets_elig = assets <= p_asset_limit
        return income_elig & assets_elig
