from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wi.dcf.shares.rates.wi_shares_provider_type import (
    WISharesProviderType,
)
from policyengine_us.variables.gov.states.wi.dcf.shares.hours.wi_shares_time_category import (
    WISharesTimeCategory,
)


class wi_shares_monthly_max_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Wisconsin Shares monthly maximum rate"
    definition_period = MONTH
    defined_for = "wi_shares_eligible_child"
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=156",
        "https://dcf.wisconsin.gov/files/wishares/pdf/max-rates-statewide.pdf#page=26",
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/III/155/6",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dcf.shares
        age_group = person("wi_shares_age_group", period)
        county = person.household("county_str", period)
        # defined_for does not short-circuit vectorized execution, so
        # non-Wisconsin counties are masked before indexing the county-keyed
        # rate tables.
        in_wi = person.household("state_code_str", period) == "WI"
        safe_county = where(in_wi, county, "ADAMS_COUNTY_WI")
        # The published part-time monthly maximum equals the hourly maximum
        # times the 131 part-time monthly hours (verified for every county),
        # so it is derived; full-time monthly maximums are independent table
        # cells (Section 18.5.1).
        part_time_monthly_hours = np.ceil(
            p.hours.part_time_weekly_conversion * p.hours.weeks_per_month
        )
        licensed_group_hourly = p.rates.licensed_group.hourly[age_group][safe_county]
        licensed_family_hourly = p.rates.licensed_family.hourly[age_group][safe_county]
        time_category = person("wi_shares_time_category", period)
        full_time = time_category == WISharesTimeCategory.FULL_TIME
        licensed_group_monthly = where(
            full_time,
            p.rates.licensed_group.full_time_monthly[age_group][safe_county],
            licensed_group_hourly * part_time_monthly_hours,
        )
        licensed_family_monthly = where(
            full_time,
            p.rates.licensed_family.full_time_monthly[age_group][safe_county],
            licensed_family_hourly * part_time_monthly_hours,
        )
        # Certified providers have no monthly maximum of their own; their
        # monthly subsidy payments are capped at the licensed family monthly
        # maximum (Section 18.5.1; Wis. Stat. § 49.155(6)(b)-(c)).
        provider_type = person("wi_shares_provider_type", period)
        return select(
            [
                provider_type == WISharesProviderType.LICENSED_GROUP,
                provider_type == WISharesProviderType.LICENSED_FAMILY,
                provider_type == WISharesProviderType.CERTIFIED,
            ],
            [
                licensed_group_monthly,
                licensed_family_monthly,
                licensed_family_monthly,
            ],
        )
