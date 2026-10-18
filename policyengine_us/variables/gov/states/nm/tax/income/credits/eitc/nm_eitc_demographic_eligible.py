from policyengine_us.model_api import *


class nm_eitc_demographic_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Meets demographic eligibility for New Mexico EITC"
    definition_period = YEAR
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        # New Mexico applies the same criteria as the federal EITC, but
        # changes the minimum age.
        person = tax_unit.members
        # A qualifying child under IRC 32(c)(3), before the identification
        # requirement that New Mexico does not apply: a dependent under 19, a
        # student under 24, or permanently and totally disabled. A filer is
        # not their own or their spouse's qualifying child. For a child under
        # 18 the count of children must also be positive, so a supplied count
        # of zero still means no children.
        filer = person("is_tax_unit_head_or_spouse", period)
        qualifying_child = person("is_eitc_qualifying_child", period)
        minor = person("is_child", period)
        minor_child = (tax_unit("tax_unit_children", period) > 0) & tax_unit.any(
            qualifying_child & minor
        )
        has_child = minor_child | tax_unit.any(qualifying_child & ~minor)
        age = person("age", period)
        # Relative parameter reference break branching in some states that
        # modify EITC age limits.
        min_age = parameters.gov.states.nm.tax.income.credits.eitc.eligibility.age.min(
            period
        )
        max_age = parameters.gov.irs.credits.eitc.eligibility.age.max(period)
        meets_age_requirements = (age >= min_age) & (age <= max_age)
        # NMSA 7-2-18.15 takes the federal credit's eligibility rules apart
        # from the age and identification exceptions. As federally (IRC
        # 32(c)(1)(A)(ii)(II)), the age test applies to the filers, not to
        # dependents. A filer without a qualifying child must not be a
        # dependent of another taxpayer (IRC 32(c)(1)(A)(ii)(III)), and on a
        # joint return neither spouse may be claimable (Publication 596,
        # Rule 12).
        dependent_filer = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        childless_eligible = (
            tax_unit.any(meets_age_requirements & filer) & ~dependent_filer
        )
        return has_child | childless_eligible
