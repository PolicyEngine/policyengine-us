from policyengine_us.model_api import *


class home_sale_gain_exclusion(Variable):
    value_type = float
    entity = Person
    label = "Excluded gain on the sale of a main home"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/121",
        "https://www.irs.gov/publications/p523",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.capital_gains.home_sale_exclusion
        gain = max_(0, person("home_sale_gain", period))
        depreciation = max_(
            0, person("home_sale_depreciation_after_may_6_1997", period)
        )
        nonqualified = np.clip(person("home_sale_nonqualified_use_share", period), 0, 1)
        excludable_gain = max_(0, gain - depreciation) * (1 - nonqualified)
        owned = person("home_sale_ownership_months", period)
        used = person("home_sale_use_months", period)
        prior = person("home_sale_excluded_gain_within_two_years", period)
        meets_full = (owned >= p.required_months) & (used >= p.required_months) & ~prior
        # Reduced exclusion: the shortest of ownership, use and time since
        # the last exclusion, over 24 months (IRC 121(c)(1)).
        since_prior = where(
            prior,
            person("home_sale_months_since_prior_exclusion", period),
            p.required_months,
        )
        fraction = np.clip(
            np.minimum(np.minimum(owned, used), since_prior) / p.required_months, 0, 1
        )
        reduced = person("home_sale_reduced_exclusion_qualifies", period) & ~meets_full
        # A married couple in one tax unit is treated as filing jointly;
        # filing_status itself depends on capital gains through dependency tests.
        joint = person.tax_unit("tax_unit_married", period)
        spouse_ok = person("home_sale_spouse_meets_use_test", period) & ~person(
            "home_sale_spouse_excluded_gain_within_two_years", period
        )
        full_limit = where(joint & spouse_ok, p.joint_amount, p.amount)
        limit = where(meets_full, full_limit, where(reduced, fraction * p.amount, 0))
        return min_(excludable_gain, limit)
