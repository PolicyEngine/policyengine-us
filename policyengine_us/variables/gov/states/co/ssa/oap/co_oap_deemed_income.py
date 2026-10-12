from policyengine_us.model_api import *


class co_oap_deemed_income(Variable):
    value_type = float
    entity = Person
    label = "Colorado Old Age Pension income deemed from a spouse"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CO
    # PDF pages 77-78
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=77"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.ssa.oap
        # 3.534(C): no income is deemed from a spouse who receives Adult
        # Financial, SSI or Medicaid with income within the OAP limit.
        deemable = ~person("co_oap_deeming_exempt", period)
        earned = person("ssi_earned_income", period) * deemable
        unearned = person("ssi_unearned_income", period) * deemable
        # 3.534(B)(5): court-ordered support obligations of the spouse. Whether
        # the income is garnished instead is not modeled.
        support = (
            add(person, period, ["child_support_expense", "alimony_expense"]) * deemable
        )
        marital_unit = person.marital_unit
        spouse_earned = marital_unit.sum(earned) - earned
        spouse_unearned = marital_unit.sum(unearned) - unearned
        spouse_support = marital_unit.sum(support) - support

        # 3.534(B)(3): for each dependent child in the household, half the SSI
        # benefit standard for an individual less the child's own income.
        year = period.this_year
        dependent_child = person("is_tax_unit_dependent", year) & person(
            "is_child", year
        )
        child_income = add(person, period, ["ssi_earned_income", "ssi_unearned_income"])
        fbr = parameters(period).gov.ssa.ssi.amount.individual
        child_allocation = dependent_child * max_(
            0, fbr * p.income.deeming.child_allocation_share - child_income
        )
        child_allocations = person.household.sum(child_allocation)

        # 3.534(A): deduct $65 from the spouse's gross earned income and halve
        # the rest. Unlike SSI (20 CFR 416.1163) there is no deeming threshold.
        deemed_earned = (
            max_(0, spouse_earned - p.income.disregards.earned)
            * p.income.disregards.earned_share
        )
        # 3.534(B): deduct the OAP grant standard, child allocations and
        # support obligations from the spouse's unearned income. Medical care
        # payments for uninsured dependents (3.534(B)(4)) are not modeled.
        deemed_unearned = max_(
            0,
            spouse_unearned - p.grant_standard - child_allocations - spouse_support,
        )
        # Sponsor deeming (3.534(D)) and the institutionalized spouse's MMMNA
        # (3.534(C)) are not modeled.
        return (deemed_earned + deemed_unearned) * (marital_unit.nb_persons() == 2)
