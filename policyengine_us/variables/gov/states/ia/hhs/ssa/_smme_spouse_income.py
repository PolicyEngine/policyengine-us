from policyengine_us.model_api import *


def smme_spouse_is_aged_blind_disabled(person, period):
    """Whether the other member of a two-person marital unit is a person SSI
    treats as aged, blind or disabled. For an applicant whom SSI does not
    count, any such member of the marital unit is the spouse."""
    abd = person("is_ssi_aged_blind_disabled", period.this_year)
    return person.marital_unit.sum(abd) - abd > 0


def smme_spouse_income(person, period):
    """A spouse's SSI earned and unearned income. For an ineligible spouse,
    allocations for ineligible children are deducted, from unearned income
    first (20 CFR 416.1163(b)(3)). A spouse whom SSI treats as aged, blind or
    disabled is not an ineligible spouse, and the couple's income is combined
    as for an eligible couple, with no allocations."""
    earned = person("ssi_earned_income", period)
    unearned = person("ssi_unearned_income", period)
    spouse_earned = person.marital_unit.sum(earned) - earned
    spouse_unearned = person.marital_unit.sum(unearned) - unearned
    allocations = add(
        person.tax_unit, period, ["ssi_ineligible_child_allocation"]
    ) * ~smme_spouse_is_aged_blind_disabled(person, period)
    unearned_left = max_(spouse_unearned - allocations, 0)
    earned_left = max_(spouse_earned - max_(allocations - spouse_unearned, 0), 0)
    return earned_left, unearned_left
