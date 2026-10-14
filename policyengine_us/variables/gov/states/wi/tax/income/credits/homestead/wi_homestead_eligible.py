from policyengine_us.model_api import *


class wi_homestead_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Wisconsin homestead credit eligibility status"
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2021/0013_homestead_tax_credit_informational_paper_13.pdf#page=7",
        # Schedule H instructions, Steps 1 and 2 and questions 1c-1d
        # PDF pages 4, 10
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleH-inst.pdf#page=4",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.credits.homestead.eligible
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period)
        elderly = age >= p.min_elderly_age
        # The claimant must be 18 or older and must be 62 or older, disabled
        # or have earned income; the Schedule H instructions add, for a
        # married couple, "The spouse that meets this definition must be the
        # claimant."
        earnings = add(person, period, p.earnings_sources)
        disabled = person("is_disabled", period)
        qualifies = (age >= p.min_age) & (elderly | disabled | (earnings > 0))
        # Wis. Stat. 71.53(2)(d) and Schedule H Step 2a: no claim by a
        # claimant who was or will be claimed as a dependent on another
        # person's federal return, unless the claimant is 62 or older.
        claimed = person("claimed_as_dependent_on_another_return", period)
        eligible_claimant = filer & qualifies & (~claimed | elderly)
        # income eligibility
        homestead_income = tax_unit("wi_homestead_income", period)
        income_eligible = homestead_income < p.max_income
        # overall eligibility
        return tax_unit.any(eligible_claimant) & income_eligible
