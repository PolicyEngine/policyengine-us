from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wi.dcf.shares.rates.wi_shares_provider_type import (
    WISharesProviderType,
)


class wi_shares_hourly_max_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Wisconsin Shares hourly maximum rate"
    definition_period = MONTH
    defined_for = "wi_shares_eligible_child"
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=156",
        "https://dcf.wisconsin.gov/files/wishares/pdf/max-rates-statewide.pdf#page=26",
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/III/155/6",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dcf.shares.rates
        age_group = person("wi_shares_age_group", period)
        county = person.household("county_str", period)
        # defined_for does not short-circuit vectorized execution, so
        # non-Wisconsin counties are masked before indexing the county-keyed
        # rate tables.
        in_wi = person.household("state_code_str", period) == "WI"
        safe_county = where(in_wi, county, "ADAMS_COUNTY_WI")
        licensed_group_rate = p.licensed_group.hourly[age_group][safe_county]
        licensed_family_rate = p.licensed_family.hourly[age_group][safe_county]
        # Certified hourly maximums are 90% of the licensed family hourly
        # maximum, rounded up to the cent (Section 18.5.1). The cents value
        # is rounded to two decimals first so float noise cannot flip the
        # ceiling in either direction.
        certified_cents = np.round(
            licensed_family_rate * p.certified_licensed_rate_ratio * 100, 2
        )
        certified_rate = np.ceil(certified_cents) / 100
        provider_type = person("wi_shares_provider_type", period)
        return select(
            [
                provider_type == WISharesProviderType.LICENSED_GROUP,
                provider_type == WISharesProviderType.LICENSED_FAMILY,
                provider_type == WISharesProviderType.CERTIFIED,
            ],
            [licensed_group_rate, licensed_family_rate, certified_rate],
        )
