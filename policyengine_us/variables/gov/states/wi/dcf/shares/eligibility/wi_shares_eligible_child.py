from policyengine_us.model_api import *


class wi_shares_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin Shares eligible child"
    definition_period = MONTH
    defined_for = StateCode.WI
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=21",
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=22",
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/III/155/1m/a",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dcf.shares.eligibility
        age = person("age", period.this_year)
        # Children under age 19 remain eligible with a verified disability if
        # they cannot care for themselves; is_disabled proxies the verified
        # status (Section 4.3). A child who turns 13 mid-eligibility-period
        # stays eligible until renewal under the grandfather rule; we don't
        # track the renewal date at the moment.
        is_disabled = person("is_disabled", period.this_year)
        age_limit = where(is_disabled, p.disabled_child_age_limit, p.child_age_limit)
        age_eligible = age < age_limit
        # The child receiving care, not the parent, must be a U.S. citizen or
        # qualified immigrant; Wisconsin's qualified-immigrant list matches
        # the federal CCDF set (Section 4.5).
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
