from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.demographic.spm_unit import *
from openfisca_us.variables.demographic.person import *


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


class ccdf_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):
        continuous_eligible = spm_unit("ccdf_continuous_eligible", period)
        total_market_rate = spm_unit.sum(
            spm_unit.members("ccdf_market_rate", period)
        )
        copay = spm_unit("ccdf_copay", period)
        return where(continuous_eligible, total_market_rate - copay, 0)


class ccdf_county_cluster(Variable):
    value_type = int
    entity = Household
    label = u"County cluster for CCDF"
    definition_period = ETERNITY

    def formula(household, period, parameters):
        county = household("county", period).decode_to_str()
        cluster_mapping = parameters(period).benefit.ccdf.county_cluster
        return cluster_mapping[county]


class ccdf_market_rate(Variable):
    value_type = float
    entity = Person
    label = u"CCDF market rate"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        county_cluster = person("ccdf_county_cluster", period)
        provider_type_group = person("provider_type_group", period)
        child_age_group = person("ccdf_age_group", period)
        duration_of_care = person("duration_of_care", period)
        market_rate_mapping = parameters(period).benefit.ccdf.amount
        return market_rate_mapping[county_cluster][provider_type_group][
            child_age_group
        ][duration_of_care]
