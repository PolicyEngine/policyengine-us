from policyengine_us.model_api import *


def smme_spouse_income(person, period):
    """A spouse's SSI earned and unearned income after allocations for
    ineligible children, which 20 CFR 416.1163(b) deduct from unearned income
    first."""
    earned = person("ssi_earned_income", period)
    unearned = person("ssi_unearned_income", period)
    spouse_earned = person.marital_unit.sum(earned) - earned
    spouse_unearned = person.marital_unit.sum(unearned) - unearned
    allocations = add(person.tax_unit, period, ["ssi_ineligible_child_allocation"])
    unearned_left = max_(spouse_unearned - allocations, 0)
    earned_left = max_(spouse_earned - max_(allocations - spouse_unearned, 0), 0)
    return earned_left, unearned_left
