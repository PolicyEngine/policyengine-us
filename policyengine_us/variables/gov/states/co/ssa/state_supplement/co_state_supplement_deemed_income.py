from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ssa.state_supplement._and_cs_client_income import (
    and_cs_client_income,
)


class co_state_supplement_deemed_income(Variable):
    value_type = float
    entity = Person
    label = "Colorado State Supplement income deemed from a spouse or parents"
    unit = USD
    definition_period = MONTH
    defined_for = "co_state_supplement_eligible"
    # PDF pages 94-95
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=94"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.ssa.state_supplement.income.disregards
        # 3.549(D)(2): the spouse's unearned income is reduced by the part of
        # the couple's combined $20 disregard the client did not use.
        earned, _, unearned_disregard, earned_disregard = and_cs_client_income(
            person, period, parameters
        )
        used_on_earnings = min_(earned_disregard, max_(0, earned - p.earned))
        remaining_disregard = max_(
            0, p.unearned - unearned_disregard - used_on_earnings
        )

        # 3.549(F): no income is deemed from a spouse or parent who receives
        # Adult Financial, SSI or Medicaid with income within the SSI limit.
        deemable = ~person("co_state_supplement_deeming_exempt", period)
        gross_earned = person("ssi_earned_income", period) * deemable
        gross_unearned = person("ssi_unearned_income", period) * deemable

        def deem(earned_income, unearned_income):
            # 3.549(C): deduct $65 from gross earned income and halve the rest.
            # 3.549(D): deduct the remaining unearned income disregard.
            # Unlike SSI (20 CFR 416.1163), there is no deeming threshold and
            # no allocation for ineligible children.
            return max_(0, earned_income - p.earned) * p.earned_share + max_(
                0, unearned_income - remaining_disregard
            )

        # 3.549(C)-(D): the client's spouse.
        marital_unit = person.marital_unit
        spouse_deemed = deem(
            marital_unit.sum(gross_earned) - gross_earned,
            marital_unit.sum(gross_unearned) - gross_unearned,
        )

        # 3.549(E): for an unemancipated child under 18, "the parents' income
        # shall be deemed using the same calculations as a spouse". The
        # parents' income is deemed in full to each child who is a client.
        year = period.this_year
        child = person("is_child", year)
        parent = person("is_parent", year) & ~child
        tax_unit = person.tax_unit
        parents_deemed = child * deem(
            tax_unit.sum(gross_earned * parent),
            tax_unit.sum(gross_unearned * parent),
        )
        return spouse_deemed + parents_deemed
