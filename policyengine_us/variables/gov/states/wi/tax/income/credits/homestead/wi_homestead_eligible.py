from policyengine_us.model_api import *


class wi_homestead_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Wisconsin homestead credit eligibility status"
    definition_period = YEAR
    reference = "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2021/0013_homestead_tax_credit_informational_paper_13.pdf#page=7"
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.credits
        # minimum age eligibility
        head_age = tax_unit("age_head", period)
        spouse_age = tax_unit("age_spouse", period)
        min_age = p.homestead.eligible.min_age
        age_eligible = (head_age >= min_age) | (spouse_age >= min_age)
        # earnings eligibility
        earnings = add(tax_unit, period, p.homestead.eligible.earnings_sources)
        has_positive_earnings = earnings > 0
        min_elderly_age = p.homestead.eligible.min_elderly_age
        head_is_elderly = head_age >= min_elderly_age
        spouse_is_elderly = spouse_age >= min_elderly_age
        is_elderly = head_is_elderly | spouse_is_elderly
        head_is_disabled = tax_unit("head_is_disabled", period)
        spouse_is_disabled = tax_unit("spouse_is_disabled", period)
        is_disabled = head_is_disabled | spouse_is_disabled
        earnings_eligible = has_positive_earnings | is_elderly | is_disabled
        # income eligibility
        homestead_income = tax_unit("wi_homestead_income", period)
        income_eligible = homestead_income < p.homestead.eligible.max_income
        # overall eligibility
        return age_eligible & earnings_eligible & income_eligible
