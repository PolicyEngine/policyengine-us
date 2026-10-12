from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.slspc.slcsp_family_tier_category import (
    family_tier_category,
)
from policyengine_us.variables.gov.aca.slspc.slcsp_family_tier_multiplier import (
    family_tier_multiplier,
)


def benchmark_premium(tax_unit, period, parameters, group, enrolled):
    """Monthly second-lowest-cost silver premium for the enrollees of one
    family on the return.

    `group` marks the family's members and `enrolled` the Marketplace
    enrollees (person-level boolean arrays). Children are ranked within the
    family, so only its three oldest children add an age-rated premium (45 CFR
    147.102(c)(1)); in family-tier states the tier is the family's own.
    """
    person = tax_unit.members
    p = parameters(period).gov.aca
    age = person("age", period.this_year)
    is_child = age <= p.slcsp.max_child_age
    child_rank = person.get_rank(tax_unit, -age, condition=group & is_child)
    charged = group & enrolled & (~is_child | (child_rank < p.max_child_count))
    base = person.household("slcsp_age_0", period)
    multiplier = person("slcsp_age_curve_multiplier", period)
    age_curve_applies = tax_unit("slcsp_age_curve_applies", period)
    age_curve = tax_unit.sum(charged * base * multiplier) * age_curve_applies
    tier_enrolled = group & enrolled
    category = family_tier_category(tax_unit, period, parameters, tier_enrolled)
    tier_multiplier = family_tier_multiplier(
        tax_unit, period, parameters, category, tier_enrolled
    )
    family_tier = where(
        tax_unit("slcsp_family_tier_applies", period),
        tax_unit.household("slcsp_age_0", period) * tier_multiplier,
        0,
    )
    return age_curve + family_tier


class aca_ptc_slcsp(Variable):
    value_type = float
    entity = TaxUnit
    label = "Benchmark silver-plan premium for the premium tax credit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/36B#b_3_B",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-3#f",
    )
    documentation = (
        "The second-lowest-cost silver plan premium offered to the coverage "
        "family (26 CFR 1.36B-3(f)): the Marketplace enrollees who are in the "
        "premium tax credit tax family. When every enrollee on the return is "
        "in it, this is slcsp itself, read directly so a supplied slcsp "
        "carries through. When an enrollee is not (one who can be claimed on "
        "another return, or a dependent of a return with such a filer), the "
        "coverage family is priced on its own: age-curve premiums with its "
        "children ranked among themselves, so its three oldest children are "
        "charged, or, where family tiers apply, its own tier. slcsp keeps "
        "every enrollee, since everyone still buys a plan."
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        enrolled = person("is_aca_marketplace_enrollee", period.this_year)
        member = person("is_aca_tax_family_member", period.this_year)
        every_enrollee_covered = ~tax_unit.any(enrolled & ~member)
        coverage_family_benchmark = benchmark_premium(
            tax_unit, period, parameters, member, enrolled
        )
        return where(
            every_enrollee_covered,
            tax_unit("slcsp", period),
            coverage_family_benchmark,
        )
