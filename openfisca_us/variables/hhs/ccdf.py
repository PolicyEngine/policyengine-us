from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.demographic.person import *
from openfisca_us.variables.demographic.household import *


class ccdf_county_cluster(Variable):
    value_type = int
    entity = Household
    label = u"County cluster for CCDF"
    definition_period = YEAR

    def formula(household, period, parameters):
        county = household("county", period).decode_to_str()
        cluster_mapping = parameters(period).hhs.ccdf.county_cluster
        return cluster_mapping[county]


class ccdf_market_rate(Variable):
    value_type = float
    entity = Person
    label = u"CCDF market rate"
    definition_period = YEAR

    def formula(person, period, parameters):
        county_cluster = person.household("ccdf_county_cluster", period)
        provider_type_group = person("provider_type_group", period)
        child_age_group = person("ccdf_age_group", period)
        duration_of_care = person("duration_of_care", period)
        market_rate_mapping = parameters(period).hhs.ccdf.amount
        return market_rate_mapping[county_cluster][provider_type_group][
            duration_of_care
        ][child_age_group]


class is_ccdf_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = u"Asset eligibility for CCDF"

    def formula(spm_unit, period, parameters):
        assets = spm_unit("spm_unit_assets", period)
        p_asset_limit = parameters(period).hhs.ccdf.asset_limit
        return assets <= p_asset_limit


class is_ccdf_age_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = u"Age eligibility for CCDF"

    def formula(person, period, parameters):
        age = person("age", period)
        age_limit = parameters(period).hhs.ccdf.age_limit
        return age < age_limit


class is_enrolled_in_ccdf(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = u"CCDF enrollment status"


class is_ccdf_initial_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = u"Initial income eligibility for CCDF"


class is_ccdf_continuous_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = u"Continuous income eligibility for CCDF"


class is_ccdf_smi_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = u"SMI eligibility for CCDF"


class is_ccdf_reason_for_care_eligible(Variale):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = u"Reason-for-care eligibility for CCDF"


class is_ccdf_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = u"Eligibility for CCDF"

    def formula(person, period, parameters):
        asset_eligible = person.spm_unit("is_ccdf_asset_eligible", period)
        age_eligible = person("is_ccdf_age_eligible", period)
        smi_eligible = person.spm_unit("is_ccdf_smi_eligible", period)
        reason_for_care_eligible = person(
            "is_ccdf_reason_for_care_eligible", period
        )

        return (
            smi_eligible
            & reason_for_care_eligible
            & asset_eligible
            & age_eligible
        )
