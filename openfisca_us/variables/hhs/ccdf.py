from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.demographic.person import *
from openfisca_us.variables.demographic.household import *
from openfisca_us.variables.expense.person import *


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


class ccdf_income(Variable):
    value_type = float
    entity = SPMUnit
    label = u"Income"
    definition_period = YEAR


class ccdf_income_to_smi_ratio(Variable):
    value_type = float
    entity = SPMUnit
    label = u"Income to SMI ratio"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        income = spm_unit("ccdf_income", period)
        smi = spm_unit("hhs_smi", period)
        return income / smi


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


class is_ccdf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = u"Income eligibility for CCDF"

    def formula(spm_unit, period, parameters):
        income_to_smi_ratio = spm_unit("ccdf_income_to_smi_ratio", period)
        p_ratio_limit = parameters(period).hhs.ccdf.income_limit_smi
        return income_to_smi_ratio <= p_ratio_limit


class meets_ccdf_activity_test(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Indicates whether parent or parents meet activity test (working/in job training/in educational program)"
    label = u"Activity test for CCDF"


class is_ccdf_reason_for_care_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether child qualifies for CCDF based on parents meeting activity test or that he/she receives or needs protective services"
    label = u"Reason-for-care eligibility for CCDF"

    def formula(person, period):
        parent_meets_ccdf_activity_test = person.spm_unit(
            "meets_ccdf_activity_test", period
        )
        child_receives_or_needs_protective_services = person(
            "receives_or_needs_protective_services", period
        )
        return (
            parent_meets_ccdf_activity_test
            | child_receives_or_needs_protective_services
        )


class is_ccdf_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = u"Eligibility for CCDF"

    def formula(person, period, parameters):
        asset_eligible = person.spm_unit("is_ccdf_asset_eligible", period)
        age_eligible = person("is_ccdf_age_eligible", period)
        income_eligible = person.spm_unit("is_ccdf_income_eligible", period)
        reason_for_care_eligible = person(
            "is_ccdf_reason_for_care_eligible", period
        )

        return (
            asset_eligible
            & age_eligible
            & income_eligible
            & reason_for_care_eligible
        )


class is_ccdf_home_based(Variable):
    value_type = bool
    default_value = False
    entity = Person
    label = u"Whether CCDF care is home-based versus center-based"
    definition_period = YEAR

    def formula(person, period, parameters):
        return (
            person("provider_type_group", period) != ProviderTypeGroup.DCC_SACC
        )


class CCDFAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOLER = "Preschooler"
    SCHOOL_AGE = "School age"


class ccdf_age_group(Variable):
    value_type = Enum
    possible_values = CCDFAgeGroup
    default_value = CCDFAgeGroup.INFANT
    entity = Person
    label = u"CCDF age group"
    definition_period = YEAR

    reference = "https://ocfs.ny.gov/main/policies/external/ocfs_2019/LCM/19-OCFS-LCM-23.pdf"

    def formula(person, period, parameters):
        age = person("age", period)
        home_based = person("is_ccdf_home_based", period)
        return select(
            [
                ((age < 1.5) & ~home_based) | ((age < 2) & home_based),
                ((age < 2) & ~home_based) | ((age < 3) & home_based),
                age < 6,
                age < 13,
            ],
            [
                CCDFAgeGroup.INFANT,
                CCDFAgeGroup.TODDLER,
                CCDFAgeGroup.PRESCHOOLER,
                CCDFAgeGroup.SCHOOL_AGE,
            ],
        )


class DurationOfCare(Enum):
    WEEKLY = "Weekly"
    DAILY = "Daily"
    PART_DAY = "Part-Day"
    HOURLY = "Hourly"


class duration_of_care(Variable):
    value_type = Enum
    possible_values = DurationOfCare
    default_value = DurationOfCare.WEEKLY
    entity = Person
    label = u"Child care duration of care"
    definition_period = YEAR

    reference = "https://ocfs.ny.gov/main/policies/external/ocfs_2019/LCM/19-OCFS-LCM-23.pdf#page=5"

    def formula(person, period):
        hours_per_day = person("childcare_hours_per_day", period)
        days_per_week = person("childcare_days_per_week", period)
        hours_per_week = hours_per_day * days_per_week
        return select(
            [
                hours_per_week >= 30,
                hours_per_day >= 6,
                hours_per_day >= 3,
                True,
            ],
            [
                DurationOfCare.WEEKLY,
                DurationOfCare.DAILY,
                DurationOfCare.PART_DAY,
                DurationOfCare.HOURLY,
            ],
        )
