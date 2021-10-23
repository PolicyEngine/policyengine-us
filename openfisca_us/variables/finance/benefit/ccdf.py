from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.demographic.spm_unit import *


class ccdf_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):
        # Get state and poverty ratio for SPM unit.
        state = spm_unit("spm_unit_state", period)
        assets = spm_unit("spm_unit_assets", period)
        # Get parameters.
        p_asset_limit = parameters(period).benefit.CCDF.eligibility.assets[
            state
        ]
        return assets <= p_asset_limit


class ccdf_initial_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):
        # Get state and poverty ratio for SPM unit.
        state = spm_unit("spm_unit_state", period)
        poverty_ratio = spm_unit("poverty_ratio", period)
        asset_eligible = spm_unit("ccdf_asset_eligible", period)
        # Get parameters.
        p_income_limit = parameters(
            period
        ).benefit.CCDF.eligibility.initial_income[state]
        # Determine eligibility by income (% poverty) and assets.
        income_eligible = poverty_ratio <= p_income_limit
        return income_eligible & asset_eligible


class ccdf_continuous_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):
        # Get state and poverty ratio for SPM unit.
        state = spm_unit("spm_unit_state", period)
        poverty_ratio = spm_unit("poverty_ratio", period)
        asset_eligible = spm_unit("ccdf_asset_eligible", period)
        # Get parameters.
        p_income_limit = parameters(
            period
        ).benefit.CCDF.eligibility.continuous_income[state]
        # Determine eligibility by income (% poverty) and assets.
        income_eligible = poverty_ratio <= p_income_limit
        return income_eligible & asset_eligible


class ccdf_copay(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):
        # Get state and poverty ratio for SPM unit.
        income = spm_unit("spm_unit_total_income", period)
        fpl = spm_unit("spm_unit_poverty_guideline", period)
        state = spm_unit("spm_unit_state", period)
        # TODO: Get parameter by county.
        p_income_share = 0.1
        income_exceeding_fpl = max_(income - fpl, 0)
        return income_exceeding_fpl * p_income_share


class ccdf_max_benefit_per_child(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = ""


class ccdf_child_age(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = ""


class ccdf_provider_type(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = ""


class ccdf_duration_of_care(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = ""


class ccdf_child_age(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = ""


class ccdf_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):
        # TODO: Split continuous from initial.
        continuous_eligible = spm_unit("ccdf_continuous_eligible", period)
        max_benefit_per_child = spm_unit("ccdf_max_benefit_per_child", period)
        copay = spm_unit("ccdf_copay", period)
        eligible_kids = spm_unit("children", period)
        # Intermediate variables.
        max_benefit = max_benefit_per_child * eligible_kids
        return where(continuous_eligible, max_benefit - copay, 0)
