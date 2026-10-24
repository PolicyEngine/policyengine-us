from policyengine_us.model_api import *


class wi_homestead_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Wisconsin homestead credit eligibility status"
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2021/0013_homestead_tax_credit_informational_paper_13.pdf#page=7",
        # Minimum age (71.53(2)(c)) and claimant qualification paths
        # (71.54(1)(dm)-(gm)).
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/viii/53/2/c",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/viii/54",
        # PDF pages 4, 10: the claimant must be 18 or older and 62 or older,
        # disabled or have earned income; either spouse may be the claimant.
        "https://www.revenue.wi.gov/TaxForms2024/2024-ScheduleH-inst.pdf#page=4",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.credits
        # Either the head or the spouse can be the claimant, who must meet
        # every test alone: 18 or older, and 62 or older, disabled or with
        # their own earned income (Wis. Stat. 71.52(1g) computes earned
        # income per claimant). A dependent's earnings do not qualify anyone.
        min_age = p.homestead.eligible.min_age
        min_elderly_age = p.homestead.eligible.min_elderly_age
        person = tax_unit.members
        earnings = add(person, period, p.homestead.eligible.earnings_sources)
        head_earnings = tax_unit.sum(earnings * person("is_tax_unit_head", period))
        spouse_earnings = tax_unit.sum(earnings * person("is_tax_unit_spouse", period))
        head_age = tax_unit("age_head", period)
        spouse_age = tax_unit("age_spouse", period)
        head_qualifies = (head_age >= min_age) & (
            (head_age >= min_elderly_age)
            | tax_unit("head_is_disabled", period)
            | (head_earnings > 0)
        )
        spouse_qualifies = (spouse_age >= min_age) & (
            (spouse_age >= min_elderly_age)
            | tax_unit("spouse_is_disabled", period)
            | (spouse_earnings > 0)
        )
        # income eligibility
        homestead_income = tax_unit("wi_homestead_income", period)
        income_eligible = homestead_income < p.homestead.eligible.max_income
        return (head_qualifies | spouse_qualifies) & income_eligible
